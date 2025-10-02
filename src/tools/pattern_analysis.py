"""
Pattern Analysis Tools

Tools for detecting temporal patterns, frequency analysis, and clustering.
"""

import pandas as pd
import numpy as np
from typing import Optional
from langchain.tools import Tool
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy import stats

from .data_description import get_dataframe, _data_processor


# ============================================================
# Tool 6: Detect Temporal Patterns
# ============================================================

def detect_temporal_patterns(input_str: str) -> str:
    """
    Detect temporal patterns and trends in time series data.
    
    Args:
        input_str: Format "date_column,value_column"
        
    Returns:
        String with temporal pattern analysis
    """
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        if len(parts) != 2:
            return "Error: Input should be 'date_column,value_column'"
        
        date_col, value_col = parts
        
        if date_col not in df.columns:
            return f"Error: Date column '{date_col}' not found"
        if value_col not in df.columns:
            return f"Error: Value column '{value_col}' not found"
        
        # Convert to datetime
        df_temp = df[[date_col, value_col]].copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
        df_temp = df_temp.dropna()
        df_temp = df_temp.sort_values(date_col)
        
        if len(df_temp) < 2:
            return "Error: Not enough valid data points for temporal analysis"
        
        result = f"📅 Temporal Pattern Analysis:\n\n"
        result += f"**Date Range:** {df_temp[date_col].min()} to {df_temp[date_col].max()}\n"
        result += f"**Total data points:** {len(df_temp)}\n\n"
        
        # Calculate trend
        df_temp['day_number'] = (df_temp[date_col] - df_temp[date_col].min()).dt.days
        
        if df_temp[value_col].dtype in ['int64', 'float64']:
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                df_temp['day_number'], df_temp[value_col]
            )
            
            result += "**Trend Analysis:**\n"
            if p_value < 0.05:
                if slope > 0:
                    result += f"  • Significant UPWARD trend detected (slope: {slope:.4f})\n"
                    result += f"  • Average increase of {slope:.4f} per day\n"
                else:
                    result += f"  • Significant DOWNWARD trend detected (slope: {slope:.4f})\n"
                    result += f"  • Average decrease of {abs(slope):.4f} per day\n"
                result += f"  • R-squared: {r_value**2:.4f} (strength of trend)\n"
            else:
                result += "  • No significant trend detected (data is relatively stable)\n"
            
            result += "\n"
            
            # Calculate rolling statistics
            if len(df_temp) >= 7:
                df_temp['rolling_mean_7'] = df_temp[value_col].rolling(window=7, min_periods=1).mean()
                df_temp['rolling_std_7'] = df_temp[value_col].rolling(window=7, min_periods=1).std()
                
                result += "**Volatility Analysis:**\n"
                recent_volatility = df_temp['rolling_std_7'].iloc[-7:].mean()
                overall_volatility = df_temp[value_col].std()
                
                result += f"  • Overall std deviation: {overall_volatility:.4f}\n"
                result += f"  • Recent (7-day) avg std: {recent_volatility:.4f}\n"
                
                if recent_volatility > overall_volatility * 1.2:
                    result += "  • ⚠️ Increased volatility recently\n"
                elif recent_volatility < overall_volatility * 0.8:
                    result += "  • ✓ Decreased volatility recently (more stable)\n"
                
                result += "\n"
            
            # Detect seasonality (if enough data)
            if len(df_temp) >= 30:
                df_temp['day_of_week'] = df_temp[date_col].dt.dayofweek
                dow_avg = df_temp.groupby('day_of_week')[value_col].mean()
                dow_std = dow_avg.std()
                
                if dow_std > df_temp[value_col].std() * 0.3:
                    result += "**Seasonality (Day of Week):**\n"
                    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    for day_num, avg_val in dow_avg.items():
                        result += f"  • {days[day_num]}: {avg_val:.2f}\n"
                    result += "  • Weekly pattern detected\n"
        
        return result
        
    except Exception as e:
        return f"Error detecting temporal patterns: {str(e)}"


detect_temporal_patterns_tool = Tool(
    name="detect_temporal_patterns",
    func=detect_temporal_patterns,
    description="""Detecte padrões temporais, tendências e sazonalidade em dados de séries temporais.
    A entrada deve ser 'date_column,value_column' (separado por vírgula).
    Exemplo: "date,sales" ou "timestamp,temperature" """
)


# ============================================================
# Tool 7: Get Frequency Analysis
# ============================================================

def get_frequency_analysis(input_str: str) -> str:
    """
    Analyze frequency distribution of values in a column.
    
    Args:
        input_str: Format "column_name" or "column_name,top_n"
        
    Returns:
        String with frequency analysis
    """
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        column_name = parts[0]
        top_n = int(parts[1]) if len(parts) > 1 else 10
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found"
        
        series = df[column_name].dropna()
        value_counts = series.value_counts()
        
        result = f"📊 Frequency Analysis for '{column_name}':\n\n"
        result += f"**Total values:** {len(series):,}\n"
        result += f"**Unique values:** {len(value_counts):,}\n\n"
        
        # Most frequent
        result += f"**Top {min(top_n, len(value_counts))} Most Frequent:**\n"
        for i, (value, count) in enumerate(value_counts.head(top_n).items(), 1):
            percentage = (count / len(series)) * 100
            result += f"{i}. {value}: {count:,} ({percentage:.2f}%)\n"
        
        result += "\n"
        
        # Least frequent
        result += f"**Bottom {min(top_n, len(value_counts))} Least Frequent:**\n"
        for i, (value, count) in enumerate(value_counts.tail(top_n).iloc[::-1].items(), 1):
            percentage = (count / len(series)) * 100
            result += f"{i}. {value}: {count:,} ({percentage:.2f}%)\n"
        
        result += "\n**Distribution Characteristics:**\n"
        
        # Calculate concentration
        top_10_pct = value_counts.head(10).sum() / len(series) * 100
        result += f"  • Top 10 values account for {top_10_pct:.1f}% of data\n"
        
        # Check if uniform
        expected_count = len(series) / len(value_counts)
        chi_square = ((value_counts - expected_count) ** 2 / expected_count).sum()
        
        if chi_square < len(value_counts):
            result += "  • Distribution is relatively uniform\n"
        else:
            result += "  • Distribution is skewed (some values dominate)\n"
        
        return result
        
    except Exception as e:
        return f"Error in frequency analysis: {str(e)}"


get_frequency_analysis_tool = Tool(
    name="get_frequency_analysis",
    func=get_frequency_analysis,
    description="""Analise a distribuição de frequência - encontre os valores mais e menos frequentes.
    A entrada deve ser 'column_name' ou 'column_name,top_n' onde top_n é o número de valores a mostrar.
    Exemplo: "category" ou "product,20" """
)


# ============================================================
# Tool 8: Detect Clusters
# ============================================================

def detect_clusters(input_str: str) -> str:
    """
    Detect clusters in the data using K-means clustering.
    
    Args:
        input_str: Format "column1,column2,..." or "column1,column2,...,n_clusters"
        
    Returns:
        String with clustering results
    """
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        
        # Check if last part is a number (n_clusters)
        try:
            n_clusters = int(parts[-1])
            columns = parts[:-1]
        except ValueError:
            n_clusters = 3  # Default
            columns = parts
        
        if not columns:
            return "Error: Please specify at least one column"
        
        # Validate columns
        invalid_cols = [c for c in columns if c not in df.columns]
        if invalid_cols:
            return f"Error: Columns not found: {', '.join(invalid_cols)}"
        
        # Select numerical columns only
        df_cluster = df[columns].copy()
        numerical_cols = []
        
        for col in columns:
            if _data_processor.detect_column_type(df_cluster[col]) == 'numerical':
                numerical_cols.append(col)
        
        if not numerical_cols:
            return "Error: No numerical columns found for clustering"
        
        df_cluster = df_cluster[numerical_cols].dropna()
        
        if len(df_cluster) < n_clusters:
            return f"Error: Not enough data points ({len(df_cluster)}) for {n_clusters} clusters"
        
        # Limit n_clusters
        n_clusters = min(n_clusters, 10, len(df_cluster) // 2)
        
        result = f"🎯 Cluster Analysis:\n\n"
        result += f"**Features used:** {', '.join(numerical_cols)}\n"
        result += f"**Data points:** {len(df_cluster):,}\n"
        result += f"**Number of clusters:** {n_clusters}\n\n"
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_cluster)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        # Calculate silhouette score
        if len(df_cluster) > n_clusters:
            sil_score = silhouette_score(X_scaled, labels)
            result += f"**Silhouette Score:** {sil_score:.3f}\n"
            
            if sil_score > 0.5:
                result += "  • ✓ Strong cluster structure\n"
            elif sil_score > 0.25:
                result += "  • Moderate cluster structure\n"
            else:
                result += "  • ⚠️ Weak cluster structure\n"
            
            result += "\n"
        
        # Describe each cluster
        df_cluster['cluster'] = labels
        
        result += "**Cluster Characteristics:**\n\n"
        
        for cluster_id in range(n_clusters):
            cluster_data = df_cluster[df_cluster['cluster'] == cluster_id]
            size = len(cluster_data)
            percentage = (size / len(df_cluster)) * 100
            
            result += f"**Cluster {cluster_id + 1}** ({size:,} points, {percentage:.1f}%):\n"
            
            for col in numerical_cols:
                mean_val = cluster_data[col].mean()
                result += f"  • {col}: {mean_val:.2f}\n"
            
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error detecting clusters: {str(e)}"


detect_clusters_tool = Tool(
    name="detect_clusters",
    func=detect_clusters,
    description="""Detecte clusters em dados numéricos usando clustering K-means.
    A entrada deve ser nomes de colunas numéricas separados por vírgula, opcionalmente com o número de clusters no final.
    Exemplo: "age,salary" ou "height,weight,income,3" (para 3 clusters)"""
)
