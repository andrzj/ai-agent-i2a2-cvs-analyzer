"""
Data Description Tools

Tools for analyzing data types, distributions, ranges, central tendency, and variability.
These tools provide statistical summaries without sending raw data to the LLM.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from langchain.tools import Tool

# Global variable to store DataFrame (will be set by the agent)
_dataframe: Optional[pd.DataFrame] = None
_data_processor = None


def set_dataframe(df: pd.DataFrame, processor):
    """Set the DataFrame for tools to operate on."""
    global _dataframe, _data_processor
    _dataframe = df
    _data_processor = processor


def get_dataframe() -> pd.DataFrame:
    """Get the current DataFrame."""
    if _dataframe is None:
        raise ValueError("No DataFrame loaded. Please upload a CSV file first.")
    return _dataframe


# ============================================================
# Tool 1: Get Data Types
# ============================================================

def get_data_types(columns: str = "") -> str:
    """
    Get the data types of columns in the dataset.
    
    Args:
        columns: Comma-separated column names (empty for all columns)
        
    Returns:
        String describing the data types
    """
    try:
        df = get_dataframe()
        
        if columns.strip():
            # Parse column names
            col_list = [c.strip() for c in columns.split(',')]
            # Validate columns exist
            invalid_cols = [c for c in col_list if c not in df.columns]
            if invalid_cols:
                return f"Error: Columns not found: {', '.join(invalid_cols)}"
        else:
            col_list = df.columns.tolist()
        
        type_info = _data_processor.analyze_data_types(df)
        
        result = "📊 Data Types Analysis:\n\n"
        
        # Group by type
        by_type = {}
        for col in col_list:
            if col in type_info:
                semantic_type = type_info[col]['semantic_type']
                if semantic_type not in by_type:
                    by_type[semantic_type] = []
                by_type[semantic_type].append({
                    'name': col,
                    'dtype': type_info[col]['pandas_dtype'],
                    'unique': type_info[col]['unique_count'],
                    'nulls': type_info[col]['null_percentage']
                })
        
        for dtype, cols in sorted(by_type.items()):
            result += f"\n**{dtype.upper()} columns ({len(cols)}):**\n"
            for col_info in cols:
                result += f"  • {col_info['name']} (dtype: {col_info['dtype']}, unique: {col_info['unique']}, nulls: {col_info['nulls']}%)\n"
        
        return result
        
    except Exception as e:
        return f"Error getting data types: {str(e)}"


get_data_types_tool = Tool(
    name="get_data_types",
    func=get_data_types,
    description="""Obtenha os tipos de dados (numérico, categórico, datetime, texto) das colunas no conjunto de dados.
    A entrada deve ser nomes de colunas separados por vírgula, ou string vazia para todas as colunas.
    Exemplo: "age,salary,department" ou "" para todas as colunas."""
)


# ============================================================
# Tool 2: Get Distribution Stats
# ============================================================

def get_distribution_stats(column_name: str) -> str:
    """
    Get distribution statistics for a specific column.
    
    Args:
        column_name: Name of the column to analyze
        
    Returns:
        String with distribution statistics
    """
    try:
        df = get_dataframe()
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found. Available columns: {', '.join(df.columns)}"
        
        summary = _data_processor.get_column_summary(df, column_name)
        
        result = f"📈 Distribution Statistics for '{column_name}':\n\n"
        result += f"Type: {summary['type']}\n"
        result += f"Count: {summary['count']:,}\n"
        result += f"Null values: {summary['null_count']:,} ({summary['null_percentage']}%)\n"
        result += f"Unique values: {summary['unique_count']:,}\n\n"
        
        if summary['type'] == 'numerical':
            result += "**Numerical Statistics:**\n"
            result += f"  • Min: {summary['min']:.2f}\n"
            result += f"  • Max: {summary['max']:.2f}\n"
            result += f"  • Mean: {summary['mean']:.2f}\n"
            result += f"  • Median: {summary['median']:.2f}\n"
            result += f"  • Std Dev: {summary['std']:.2f}\n"
            result += f"  • 25th percentile: {summary['q25']:.2f}\n"
            result += f"  • 75th percentile: {summary['q75']:.2f}\n"
            
        elif summary['type'] == 'categorical':
            result += "**Top Values:**\n"
            for value, count in list(summary['top_values'].items())[:10]:
                percentage = (count / summary['count']) * 100
                result += f"  • {value}: {count:,} ({percentage:.1f}%)\n"
                
        elif summary['type'] == 'datetime':
            result += "**Date Range:**\n"
            result += f"  • Earliest: {summary.get('min_date', 'N/A')}\n"
            result += f"  • Latest: {summary.get('max_date', 'N/A')}\n"
            result += f"  • Range: {summary.get('date_range_days', 0):,} days\n"
        
        return result
        
    except Exception as e:
        return f"Error getting distribution stats: {str(e)}"


get_distribution_stats_tool = Tool(
    name="get_distribution_stats",
    func=get_distribution_stats,
    description="""Obtenha estatísticas de distribuição (média, mediana, moda, desvio padrão, variância, quartis) para uma coluna específica.
    A entrada deve ser um único nome de coluna.
    Exemplo: "age" ou "salary" """
)


# ============================================================
# Tool 3: Get Range Info
# ============================================================

def get_range_info(columns: str) -> str:
    """
    Get range information (min, max) for specified columns.
    
    Args:
        columns: Comma-separated column names
        
    Returns:
        String with range information
    """
    try:
        df = get_dataframe()
        
        col_list = [c.strip() for c in columns.split(',') if c.strip()]
        
        if not col_list:
            return "Error: Please specify at least one column name"
        
        result = "📏 Range Information:\n\n"
        
        for col in col_list:
            if col not in df.columns:
                result += f"❌ Column '{col}' not found\n\n"
                continue
            
            series = df[col]
            col_type = _data_processor.detect_column_type(series)
            
            result += f"**{col}** ({col_type}):\n"
            
            if col_type == 'numerical':
                min_val = series.min()
                max_val = series.max()
                range_val = max_val - min_val
                result += f"  • Min: {min_val:.2f}\n"
                result += f"  • Max: {max_val:.2f}\n"
                result += f"  • Range: {range_val:.2f}\n"
                
            elif col_type == 'categorical':
                result += f"  • Unique values: {series.nunique()}\n"
                result += f"  • Most common: {series.mode().iloc[0] if len(series.mode()) > 0 else 'N/A'}\n"
                result += f"  • Least common: {series.value_counts().idxmin()}\n"
                
            elif col_type == 'datetime':
                try:
                    dt_series = pd.to_datetime(series, errors='coerce')
                    result += f"  • Earliest: {dt_series.min()}\n"
                    result += f"  • Latest: {dt_series.max()}\n"
                    result += f"  • Span: {(dt_series.max() - dt_series.min()).days} days\n"
                except:
                    result += f"  • Unable to parse as datetime\n"
            
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error getting range info: {str(e)}"


get_range_info_tool = Tool(
    name="get_range_info",
    func=get_range_info,
    description="""Obtenha informações de intervalo (mínimo, máximo, amplitude) para uma ou mais colunas.
    A entrada deve ser nomes de colunas separados por vírgula.
    Exemplo: "age,salary,price" """
)


# ============================================================
# Tool 4: Calculate Central Tendency
# ============================================================

def calculate_central_tendency(column_name: str) -> str:
    """
    Calculate measures of central tendency for a column.
    
    Args:
        column_name: Name of the column
        
    Returns:
        String with central tendency measures
    """
    try:
        df = get_dataframe()
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found"
        
        series = df[column_name].dropna()
        col_type = _data_processor.detect_column_type(series)
        
        result = f"📊 Central Tendency for '{column_name}':\n\n"
        
        if col_type == 'numerical':
            mean = series.mean()
            median = series.median()
            
            # Calculate mode (can be multiple values)
            mode_values = series.mode()
            
            result += f"**Mean:** {mean:.4f}\n"
            result += f"**Median:** {median:.4f}\n"
            
            if len(mode_values) > 0:
                if len(mode_values) == 1:
                    result += f"**Mode:** {mode_values.iloc[0]:.4f}\n"
                else:
                    result += f"**Modes:** {', '.join([f'{m:.4f}' for m in mode_values[:5]])}\n"
            
            result += f"\n**Interpretation:**\n"
            
            # Interpret the relationship
            if abs(mean - median) < series.std() * 0.1:
                result += "  • Distribution appears roughly symmetric (mean ≈ median)\n"
            elif mean > median:
                result += "  • Distribution is right-skewed (mean > median)\n"
                result += "  • Presence of high outliers pulling the mean up\n"
            else:
                result += "  • Distribution is left-skewed (mean < median)\n"
                result += "  • Presence of low outliers pulling the mean down\n"
                
        elif col_type == 'categorical':
            mode_value = series.mode().iloc[0] if len(series.mode()) > 0 else None
            mode_count = series.value_counts().iloc[0] if len(series.value_counts()) > 0 else 0
            mode_pct = (mode_count / len(series)) * 100
            
            result += f"**Mode (most common):** {mode_value}\n"
            result += f"**Frequency:** {mode_count:,} ({mode_pct:.1f}%)\n"
            result += f"**Unique values:** {series.nunique()}\n"
        else:
            result += f"Central tendency measures are not applicable for {col_type} type.\n"
        
        return result
        
    except Exception as e:
        return f"Error calculating central tendency: {str(e)}"


calculate_central_tendency_tool = Tool(
    name="calculate_central_tendency",
    func=calculate_central_tendency,
    description="""Calcule medidas de tendência central (média, mediana, moda) para uma coluna com interpretação.
    A entrada deve ser um único nome de coluna.
    Exemplo: "age" ou "salary" """
)


# ============================================================
# Tool 5: Calculate Variability
# ============================================================

def calculate_variability(column_name: str) -> str:
    """
    Calculate measures of variability/dispersion for a column.
    
    Args:
        column_name: Name of the column
        
    Returns:
        String with variability measures
    """
    try:
        df = get_dataframe()
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found"
        
        series = df[column_name].dropna()
        col_type = _data_processor.detect_column_type(series)
        
        result = f"📉 Variability Measures for '{column_name}':\n\n"
        
        if col_type == 'numerical':
            std = series.std()
            variance = series.var()
            range_val = series.max() - series.min()
            iqr = series.quantile(0.75) - series.quantile(0.25)
            
            # Coefficient of variation (only if mean is not zero)
            mean = series.mean()
            cv = (std / mean * 100) if mean != 0 else float('inf')
            
            result += f"**Standard Deviation:** {std:.4f}\n"
            result += f"**Variance:** {variance:.4f}\n"
            result += f"**Range:** {range_val:.4f}\n"
            result += f"**Interquartile Range (IQR):** {iqr:.4f}\n"
            
            if cv != float('inf'):
                result += f"**Coefficient of Variation:** {cv:.2f}%\n"
            
            result += f"\n**Interpretation:**\n"
            
            # Interpret variability
            if cv < 15:
                result += "  • Low variability - data points are clustered close to the mean\n"
            elif cv < 30:
                result += "  • Moderate variability - reasonable spread around the mean\n"
            else:
                result += "  • High variability - data points are widely dispersed\n"
            
            # Compare std to range
            if std / range_val < 0.25:
                result += "  • Most data is concentrated in a narrow range\n"
            
        elif col_type == 'categorical':
            value_counts = series.value_counts()
            entropy = -(value_counts / len(series) * np.log2(value_counts / len(series))).sum()
            max_entropy = np.log2(series.nunique())
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            
            result += f"**Unique values:** {series.nunique()}\n"
            result += f"**Entropy:** {entropy:.4f}\n"
            result += f"**Normalized entropy:** {normalized_entropy:.4f}\n"
            
            result += f"\n**Interpretation:**\n"
            if normalized_entropy > 0.8:
                result += "  • High diversity - values are fairly evenly distributed\n"
            elif normalized_entropy > 0.5:
                result += "  • Moderate diversity - some values dominate but others present\n"
            else:
                result += "  • Low diversity - few values dominate the distribution\n"
        else:
            result += f"Variability measures are not applicable for {col_type} type.\n"
        
        return result
        
    except Exception as e:
        return f"Error calculating variability: {str(e)}"


calculate_variability_tool = Tool(
    name="calculate_variability",
    func=calculate_variability,
    description="""Calcule medidas de variabilidade (desvio padrão, variância, IQR, coeficiente de variação) para uma coluna.
    A entrada deve ser um único nome de coluna.
    Exemplo: "age" ou "price" """
)
