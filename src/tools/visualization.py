"""
Visualization Tools

Tools for creating interactive visualizations using Plotly.
Returns JSON representations that can be displayed in Streamlit.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import logging
from typing import Optional
from langchain.tools import Tool
import json

from .data_description import get_dataframe
from config.settings import Settings

logger = logging.getLogger(__name__)


def _is_numerical_column(series: pd.Series) -> bool:
    """Check if a series is numerical."""
    return pd.api.types.is_numeric_dtype(series)


# ============================================================
# Tool 15: Create Histogram
# ============================================================

def create_histogram(input_str: str) -> str:
    """Create a histogram for a numerical column."""
    try:
        logger.info(f"create_histogram called with input: {input_str}")
        df = get_dataframe()
        logger.info(f"DataFrame retrieved: shape={df.shape}")
        
        parts = [p.strip() for p in input_str.split(',')]
        column_name = parts[0]
        bins = int(parts[1]) if len(parts) > 1 else Settings.DEFAULT_HISTOGRAM_BINS
        logger.info(f"Parsed: column={column_name}, bins={bins}")
        
        if column_name not in df.columns:
            error_msg = f"Error: Column '{column_name}' not found"
            logger.error(error_msg)
            return error_msg
        
        series = df[column_name].dropna()
        
        if not _is_numerical_column(series):
            return f"Error: Column '{column_name}' must be numerical for histogram (dtype: {series.dtype})"
        
        # Create histogram using plotly
        fig = px.histogram(
            df, 
            x=column_name,
            nbins=bins,
            title=f'Distribution of {column_name}',
            labels={column_name: column_name, 'count': 'Frequency'},
            template='plotly_white'
        )
        
        fig.update_layout(
            width=Settings.DEFAULT_PLOT_WIDTH,
            height=Settings.DEFAULT_PLOT_HEIGHT,
            showlegend=False
        )
        
        # Return JSON representation
        fig_json = fig.to_json()
        logger.info(f"Histogram created successfully, JSON length: {len(fig_json)} chars")
        
        result = f"PLOT_JSON:{fig_json}"
        logger.info(f"Returning result with PLOT_JSON prefix, total length: {len(result)} chars")
        return result
        
    except Exception as e:
        error_msg = f"Error creating histogram: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg


create_histogram_tool = Tool(
    name="create_histogram",
    func=create_histogram,
    description="""Crie um histograma para visualizar a distribuição de uma coluna numérica.
    A entrada deve ser 'column_name' ou 'column_name,bins' onde bins é o número de intervalos (padrão 30).
    Exemplo: "age" ou "salary,50" """
)


# ============================================================
# Tool 16: Create Scatter Plot
# ============================================================

def create_scatter_plot(input_str: str) -> str:
    """Create a scatter plot for two numerical columns."""
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        if len(parts) < 2:
            return "Error: Need at least two columns for scatter plot"
        
        x_col = parts[0]
        y_col = parts[1]
        color_col = parts[2] if len(parts) > 2 else None
        
        if x_col not in df.columns:
            return f"Error: Column '{x_col}' not found"
        if y_col not in df.columns:
            return f"Error: Column '{y_col}' not found"
        if color_col and color_col not in df.columns:
            return f"Error: Column '{color_col}' not found"
        
        # Create scatter plot
        if color_col:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f'{y_col} vs {x_col} (colored by {color_col})',
                labels={x_col: x_col, y_col: y_col},
                template='plotly_white',
                opacity=0.7
            )
        else:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                title=f'{y_col} vs {x_col}',
                labels={x_col: x_col, y_col: y_col},
                template='plotly_white',
                opacity=0.7
            )
        
        fig.update_layout(
            width=Settings.DEFAULT_PLOT_WIDTH,
            height=Settings.DEFAULT_PLOT_HEIGHT
        )
        
        # Add trendline annotation
        df_temp = df[[x_col, y_col]].dropna()
        if len(df_temp) > 1:
            from scipy.stats import pearsonr
            corr, _ = pearsonr(df_temp[x_col], df_temp[y_col])
            fig.add_annotation(
                text=f"Correlation: {corr:.3f}",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                bgcolor="white",
                bordercolor="black",
                borderwidth=1
            )
        
        fig_json = fig.to_json()
        return f"PLOT_JSON:{fig_json}"
        
    except Exception as e:
        return f"Error creating scatter plot: {str(e)}"


create_scatter_plot_tool = Tool(
    name="create_scatter_plot",
    func=create_scatter_plot,
    description="""Crie um gráfico de dispersão para visualizar o relacionamento entre duas colunas numéricas.
    A entrada deve ser 'x_column,y_column' ou 'x_column,y_column,color_column'.
    Exemplo: "age,salary" ou "height,weight,gender" """
)


# ============================================================
# Tool 17: Create Correlation Heatmap
# ============================================================

def create_correlation_heatmap(columns: str = "") -> str:
    """Create a correlation heatmap for numerical columns."""
    try:
        df = get_dataframe()
        
        if columns.strip():
            col_list = [c.strip() for c in columns.split(',')]
        else:
            # Get all numerical columns
            col_list = [col for col in df.columns if _is_numerical_column(df[col])]
        
        if len(col_list) < 2:
            return "Error: Need at least 2 numerical columns for correlation heatmap"
        
        # Select numerical columns and calculate correlation
        df_corr = df[col_list].select_dtypes(include=[np.number])
        corr_matrix = df_corr.corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            labels=dict(color="Correlation"),
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            title='Correlation Heatmap',
            template='plotly_white'
        )
        
        # Add correlation values as text
        fig.update_traces(
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10}
        )
        
        fig.update_layout(
            width=max(Settings.DEFAULT_PLOT_WIDTH, len(col_list) * 60),
            height=max(Settings.DEFAULT_PLOT_HEIGHT, len(col_list) * 60)
        )
        
        fig_json = fig.to_json()
        return f"PLOT_JSON:{fig_json}"
        
    except Exception as e:
        return f"Error creating correlation heatmap: {str(e)}"


create_correlation_heatmap_tool = Tool(
    name="create_correlation_heatmap",
    func=create_correlation_heatmap,
    description="""Crie um mapa de calor de correlação para visualizar correlações entre colunas numéricas.
    A entrada deve ser nomes de colunas separados por vírgula, ou vazio para todas as colunas numéricas.
    Exemplo: "age,salary,experience" ou "" para todas as colunas numéricas"""
)


# ============================================================
# Tool 18: Create Box Plot
# ============================================================

def create_box_plot(input_str: str) -> str:
    """Create a box plot for outlier visualization."""
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        column_name = parts[0]
        group_by = parts[1] if len(parts) > 1 else None
        
        if column_name not in df.columns:
            return f"Error: Column '{column_name}' not found"
        
        if group_by and group_by not in df.columns:
            return f"Error: Group column '{group_by}' not found"
        
        # Create box plot
        if group_by:
            fig = px.box(
                df,
                y=column_name,
                x=group_by,
                title=f'Box Plot of {column_name} by {group_by}',
                labels={column_name: column_name, group_by: group_by},
                template='plotly_white',
                points='outliers'  # Show outlier points
            )
        else:
            fig = px.box(
                df,
                y=column_name,
                title=f'Box Plot of {column_name}',
                labels={column_name: column_name},
                template='plotly_white',
                points='outliers'
            )
        
        fig.update_layout(
            width=Settings.DEFAULT_PLOT_WIDTH,
            height=Settings.DEFAULT_PLOT_HEIGHT
        )
        
        fig_json = fig.to_json()
        return f"PLOT_JSON:{fig_json}"
        
    except Exception as e:
        return f"Error creating box plot: {str(e)}"


create_box_plot_tool = Tool(
    name="create_box_plot",
    func=create_box_plot,
    description="""Crie um gráfico de caixa (box plot) para visualizar distribuição e outliers.
    A entrada deve ser 'column_name' ou 'column_name,group_by_column'.
    Exemplo: "salary" ou "salary,department" """
)


# ============================================================
# Tool 19: Create Time Series Plot
# ============================================================

def create_time_series_plot(input_str: str) -> str:
    """Create a time series line plot."""
    try:
        df = get_dataframe()
        
        parts = [p.strip() for p in input_str.split(',')]
        if len(parts) < 2:
            return "Error: Need date column and value column"
        
        date_col = parts[0]
        value_col = parts[1]
        
        if date_col not in df.columns:
            return f"Error: Date column '{date_col}' not found"
        if value_col not in df.columns:
            return f"Error: Value column '{value_col}' not found"
        
        # Prepare data
        df_temp = df[[date_col, value_col]].copy()
        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
        df_temp = df_temp.dropna()
        df_temp = df_temp.sort_values(date_col)
        
        if len(df_temp) < 2:
            return "Error: Not enough valid data points for time series"
        
        # Create line plot
        fig = px.line(
            df_temp,
            x=date_col,
            y=value_col,
            title=f'{value_col} over Time',
            labels={date_col: 'Date', value_col: value_col},
            template='plotly_white'
        )
        
        # Add markers
        fig.update_traces(mode='lines+markers', marker=dict(size=4))
        
        fig.update_layout(
            width=Settings.DEFAULT_PLOT_WIDTH,
            height=Settings.DEFAULT_PLOT_HEIGHT,
            hovermode='x unified'
        )
        
        fig_json = fig.to_json()
        return f"PLOT_JSON:{fig_json}"
        
    except Exception as e:
        return f"Error creating time series plot: {str(e)}"


create_time_series_plot_tool = Tool(
    name="create_time_series_plot",
    func=create_time_series_plot,
    description="""Crie um gráfico de linha de série temporal para visualizar tendências ao longo do tempo.
    A entrada deve ser 'date_column,value_column' (separado por vírgula).
    Exemplo: "date,sales" ou "timestamp,temperature" """
)
