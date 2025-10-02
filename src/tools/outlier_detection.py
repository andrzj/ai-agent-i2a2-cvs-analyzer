"""
Outlier Detection Tools

Tools for detecting outliers using IQR and Z-score methods, and analyzing their impact.
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional
from langchain.tools import Tool

from .data_description import get_dataframe
from config.settings import Settings

logger = logging.getLogger(__name__)


def _is_numerical_column(series: pd.Series) -> bool:
    """Check if a series is numerical."""
    return pd.api.types.is_numeric_dtype(series)


# ============================================================
# Tool 9: Detect Outliers (IQR Method)
# ============================================================

def detect_outliers_iqr(column_name: str) -> str:
    """Detect outliers using the IQR (Interquartile Range) method."""
    try:
        logger.info(f"Detecting outliers in column: {column_name}")
        df = get_dataframe()
        logger.debug(f"DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")
        
        if column_name not in df.columns:
            error_msg = f"Error: Column '{column_name}' not found. Available columns: {', '.join(df.columns.tolist())}"
            logger.error(error_msg)
            return error_msg
        
        series = df[column_name].dropna()
        logger.debug(f"Series length after dropna: {len(series)}")
        
        if not _is_numerical_column(series):
            error_msg = f"Error: Column '{column_name}' is not numerical (dtype: {series.dtype})"
            logger.error(error_msg)
            return error_msg
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - Settings.IQR_MULTIPLIER * IQR
        upper_bound = Q3 + Settings.IQR_MULTIPLIER * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        outlier_indices = outliers.index.tolist()
        
        result = f"🔍 Outlier Detection (IQR Method) for '{column_name}':\n\n"
        result += f"**Q1 (25th percentile):** {Q1:.2f}\n"
        result += f"**Q3 (75th percentile):** {Q3:.2f}\n"
        result += f"**IQR:** {IQR:.2f}\n"
        result += f"**Lower bound:** {lower_bound:.2f}\n"
        result += f"**Upper bound:** {upper_bound:.2f}\n\n"
        
        result += f"**Outliers found:** {len(outliers)} ({len(outliers)/len(series)*100:.2f}%)\n\n"
        
        if len(outliers) > 0:
            result += "**Outlier Statistics:**\n"
            result += f"  • Min outlier: {outliers.min():.2f}\n"
            result += f"  • Max outlier: {outliers.max():.2f}\n"
            result += f"  • Mean of outliers: {outliers.mean():.2f}\n\n"
            
            # Show sample outliers
            result += "**Sample outliers (up to 10):**\n"
            for idx, val in list(outliers.head(10).items()):
                result += f"  • Index {idx}: {val:.2f}\n"
            
            if len(outliers) > 10:
                result += f"  ... and {len(outliers) - 10} more\n"
        else:
            result += "✓ No outliers detected using IQR method\n"
        
        logger.info(f"Outlier detection completed for {column_name}: {len(outliers)} outliers found")
        return result
        
    except Exception as e:
        error_msg = f"Error detecting outliers: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


detect_outliers_iqr_tool = Tool(
    name="detect_outliers_iqr",
    func=detect_outliers_iqr,
    description="""Detecte outliers em uma coluna numérica usando o método IQR (Intervalo Interquartil).
    A entrada deve ser um único nome de coluna numérica.
    Exemplo: "salary" ou "age" """
)


# ============================================================
# Tool 10: Detect Outliers (Z-score Method)
# ============================================================

def detect_outliers_zscore(input_str: str) -> str:
    """Detect outliers using the Z-score method."""
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        column_name = parts[0]
        threshold = float(parts[1]) if len(parts) > 1 else Settings.ZSCORE_THRESHOLD
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found"
        
        series = df[column_name].dropna()
        
        if not _is_numerical_column(series):
            return f"Error: Column '{column_name}' is not numerical (dtype: {series.dtype})"
        
        mean = series.mean()
        std = series.std()
        
        z_scores = np.abs((series - mean) / std)
        outliers = series[z_scores > threshold]
        outlier_z_scores = z_scores[z_scores > threshold]
        
        result = f"🔍 Outlier Detection (Z-score Method) for '{column_name}':\n\n"
        result += f"**Mean:** {mean:.2f}\n"
        result += f"**Std deviation:** {std:.2f}\n"
        result += f"**Z-score threshold:** {threshold}\n\n"
        
        result += f"**Outliers found:** {len(outliers)} ({len(outliers)/len(series)*100:.2f}%)\n\n"
        
        if len(outliers) > 0:
            result += "**Outlier Statistics:**\n"
            result += f"  • Min outlier: {outliers.min():.2f}\n"
            result += f"  • Max outlier: {outliers.max():.2f}\n"
            result += f"  • Max Z-score: {outlier_z_scores.max():.2f}\n\n"
            
            # Show sample outliers with their z-scores
            result += "**Sample outliers with Z-scores (up to 10):**\n"
            sample_outliers = list(zip(outliers.head(10).items(), outlier_z_scores.head(10)))
            for (idx, val), z_score in sample_outliers:
                result += f"  • Index {idx}: {val:.2f} (Z-score: {z_score:.2f})\n"
            
            if len(outliers) > 10:
                result += f"  ... and {len(outliers) - 10} more\n"
        else:
            result += "✓ No outliers detected using Z-score method\n"
        
        return result
        
    except Exception as e:
        return f"Error detecting outliers: {str(e)}"


detect_outliers_zscore_tool = Tool(
    name="detect_outliers_zscore",
    func=detect_outliers_zscore,
    description="""Detecte outliers usando o método Z-score (valores a mais de N desvios padrão da média).
    A entrada deve ser 'column_name' ou 'column_name,threshold' (limiar padrão: 3).
    Exemplo: "salary" ou "age,2.5" """
)


# ============================================================
# Tool 11: Analyze Outlier Impact
# ============================================================

def analyze_outlier_impact(column_name: str) -> str:
    """Analyze the impact of outliers on statistical measures."""
    try:
        df = get_dataframe()
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found"
        
        series = df[column_name].dropna()
        
        if not _is_numerical_column(series):
            return f"Error: Column '{column_name}' is not numerical (dtype: {series.dtype})"
        
        # Calculate statistics with outliers
        mean_with = series.mean()
        median_with = series.median()
        std_with = series.std()
        
        # Identify outliers using IQR
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - Settings.IQR_MULTIPLIER * IQR
        upper_bound = Q3 + Settings.IQR_MULTIPLIER * IQR
        
        # Remove outliers
        series_no_outliers = series[(series >= lower_bound) & (series <= upper_bound)]
        outlier_count = len(series) - len(series_no_outliers)
        
        if outlier_count == 0:
            return f"No outliers found in '{column_name}' using IQR method"
        
        # Calculate statistics without outliers
        mean_without = series_no_outliers.mean()
        median_without = series_no_outliers.median()
        std_without = series_no_outliers.std()
        
        result = f"📊 Outlier Impact Analysis for '{column_name}':\n\n"
        result += f"**Outliers detected:** {outlier_count} ({outlier_count/len(series)*100:.2f}%)\n\n"
        
        result += "**Statistics Comparison:**\n\n"
        
        # Mean
        mean_change = abs(mean_with - mean_without)
        mean_pct_change = (mean_change / mean_with * 100) if mean_with != 0 else 0
        result += f"**Mean:**\n"
        result += f"  • With outliers: {mean_with:.2f}\n"
        result += f"  • Without outliers: {mean_without:.2f}\n"
        result += f"  • Change: {mean_change:.2f} ({mean_pct_change:.2f}%)\n\n"
        
        # Median
        median_change = abs(median_with - median_without)
        median_pct_change = (median_change / median_with * 100) if median_with != 0 else 0
        result += f"**Median:**\n"
        result += f"  • With outliers: {median_with:.2f}\n"
        result += f"  • Without outliers: {median_without:.2f}\n"
        result += f"  • Change: {median_change:.2f} ({median_pct_change:.2f}%)\n\n"
        
        # Standard Deviation
        std_change = abs(std_with - std_without)
        std_pct_change = (std_change / std_with * 100) if std_with != 0 else 0
        result += f"**Standard Deviation:**\n"
        result += f"  • With outliers: {std_with:.2f}\n"
        result += f"  • Without outliers: {std_without:.2f}\n"
        result += f"  • Change: {std_change:.2f} ({std_pct_change:.2f}%)\n\n"
        
        # Recommendations
        result += "**Recommendations:**\n"
        
        if mean_pct_change > 10:
            result += "  • ⚠️ Outliers significantly affect the mean - consider using median\n"
        else:
            result += "  • ✓ Mean is relatively robust to outliers\n"
        
        if median_pct_change > 5:
            result += "  • ⚠️ Outliers affect even the median\n"
        else:
            result += "  • ✓ Median is robust to outliers\n"
        
        if std_pct_change > 20:
            result += "  • ⚠️ Outliers greatly increase variability\n"
        
        if outlier_count / len(series) > 0.05:
            result += "  • Consider investigating the cause of outliers\n"
            result += "  • Outliers might represent: data errors, special cases, or natural variation\n"
        else:
            result += "  • Small number of outliers - likely natural variation\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Error analyzing outlier impact: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


analyze_outlier_impact_tool = Tool(
    name="analyze_outlier_impact",
    func=analyze_outlier_impact,
    description="""Analise como os outliers afetam as medidas estatísticas (média, mediana, desvio padrão) comparando com/sem outliers.
    A entrada deve ser um único nome de coluna numérica.
    Exemplo: "price" ou "salary" """
)


# ============================================================
# Tool 12: Detect Outliers in All Numerical Columns
# ============================================================

def detect_all_outliers(method: str = "iqr") -> str:
    """Detect outliers across all numerical columns in the dataset."""
    try:
        logger.info(f"Detecting outliers in all numerical columns using {method} method")
        df = get_dataframe()
        
        # Get numerical columns
        numerical_cols = []
        for col in df.columns:
            series = df[col].dropna()
            if len(series) > 0 and _is_numerical_column(series):
                numerical_cols.append(col)
        
        logger.info(f"Found {len(numerical_cols)} numerical columns")
        
        if not numerical_cols:
            return "No numerical columns found in the dataset."
        
        result = f"🔍 **Outlier Detection Summary** (using {method.upper()} method)\n\n"
        result += f"Analyzed {len(numerical_cols)} numerical columns:\n\n"
        
        outlier_summary = []
        
        for col in numerical_cols:
            series = df[col].dropna()
            
            if method.lower() == "iqr":
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - Settings.IQR_MULTIPLIER * IQR
                upper_bound = Q3 + Settings.IQR_MULTIPLIER * IQR
                outliers = series[(series < lower_bound) | (series > upper_bound)]
            else:  # zscore
                mean = series.mean()
                std = series.std()
                z_scores = np.abs((series - mean) / std)
                outliers = series[z_scores > Settings.ZSCORE_THRESHOLD]
            
            outlier_count = len(outliers)
            outlier_pct = (outlier_count / len(series)) * 100
            
            outlier_summary.append({
                'column': col,
                'count': outlier_count,
                'percentage': outlier_pct,
                'has_outliers': outlier_count > 0
            })
        
        # Sort by outlier count (descending)
        outlier_summary.sort(key=lambda x: x['count'], reverse=True)
        
        # Display summary
        columns_with_outliers = [s for s in outlier_summary if s['has_outliers']]
        columns_without_outliers = [s for s in outlier_summary if not s['has_outliers']]
        
        result += f"**Columns with outliers:** {len(columns_with_outliers)}/{len(numerical_cols)}\n\n"
        
        if columns_with_outliers:
            result += "**Outlier Details:**\n"
            for s in columns_with_outliers:
                result += f"  • **{s['column']}**: {s['count']} outliers ({s['percentage']:.2f}%)\n"
            
            # Highlight columns with high outlier percentage
            high_outlier_cols = [s for s in columns_with_outliers if s['percentage'] > 5]
            if high_outlier_cols:
                result += f"\n⚠️ **High outlier percentage (>5%):**\n"
                for s in high_outlier_cols:
                    result += f"  • {s['column']}: {s['percentage']:.1f}%\n"
        else:
            result += "✓ No outliers detected in any numerical column.\n"
        
        if columns_without_outliers:
            result += f"\n**Columns without outliers:** {len(columns_without_outliers)}\n"
            # Show first 10
            for s in columns_without_outliers[:10]:
                result += f"  • {s['column']}\n"
            if len(columns_without_outliers) > 10:
                result += f"  ... and {len(columns_without_outliers) - 10} more\n"
        
        result += f"\n💡 **Tip:** Use `detect_outliers_iqr` or `detect_outliers_zscore` to analyze a specific column in detail."
        
        logger.info(f"Outlier detection completed: {len(columns_with_outliers)} columns with outliers")
        return result
        
    except Exception as e:
        error_msg = f"Error detecting outliers in all columns: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


detect_all_outliers_tool = Tool(
    name="detect_all_outliers",
    func=detect_all_outliers,
    description="""Detecte outliers em TODAS as colunas numéricas do conjunto de dados de uma vez. 
    Isso fornece uma visão resumida de quais colunas têm outliers.
    A entrada deve ser 'iqr' ou 'zscore' para o método de detecção (padrão: iqr).
    Use isso quando perguntado sobre outliers em geral ou em todo o conjunto de dados.
    Exemplo: "iqr" ou "zscore" """
)
