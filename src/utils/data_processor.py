"""
Data Processor Module

Handles data type detection, missing value analysis, data cleaning,
and generation of data summaries for analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from config.settings import Settings


class DataProcessor:
    """
    Utility class for processing and analyzing DataFrame structure.
    
    Provides:
    - Automatic data type detection
    - Missing value analysis
    - Data summary generation
    - Smart sampling strategies
    """
    
    def __init__(self):
        """Initialize Data Processor."""
        self.settings = Settings
    
    def detect_column_type(self, series: pd.Series) -> str:
        """
        Detect the semantic type of a column.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Column type: 'numerical', 'categorical', 'datetime', or 'text'
        """
        # Skip if all values are null
        if series.isna().all():
            return 'unknown'
        
        # Check if already datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        
        # Try to infer datetime
        if series.dtype == 'object':
            # Sample non-null values
            sample = series.dropna().head(100)
            if len(sample) > 0:
                try:
                    pd.to_datetime(sample, errors='raise')
                    return 'datetime'
                except (ValueError, TypeError):
                    pass
        
        # Check if numerical
        if pd.api.types.is_numeric_dtype(series):
            # Further classify as discrete or continuous
            unique_count = series.nunique()
            total_count = len(series.dropna())
            
            if total_count == 0:
                return 'numerical'
            
            unique_ratio = unique_count / total_count
            
            # If few unique values, might be categorical
            if unique_count <= self.settings.CATEGORICAL_THRESHOLD and unique_ratio < 0.05:
                return 'categorical'
            
            return 'numerical'
        
        # Check if categorical
        if series.dtype == 'object' or series.dtype.name == 'category':
            unique_count = series.nunique()
            
            # If too many unique values, treat as text
            if unique_count > self.settings.CATEGORICAL_THRESHOLD:
                return 'text'
            
            return 'categorical'
        
        # Boolean
        if pd.api.types.is_bool_dtype(series):
            return 'categorical'
        
        return 'unknown'
    
    def analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze data types for all columns in the DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping column names to type information
        """
        type_info = {}
        
        for column in df.columns:
            series = df[column]
            semantic_type = self.detect_column_type(series)
            
            type_info[column] = {
                'semantic_type': semantic_type,
                'pandas_dtype': str(series.dtype),
                'unique_count': series.nunique(),
                'null_count': series.isna().sum(),
                'null_percentage': round(series.isna().sum() / len(series) * 100, 2)
            }
        
        return type_info
    
    def get_column_summary(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Get detailed summary for a specific column.
        
        Args:
            df: DataFrame containing the column
            column: Column name
            
        Returns:
            Dictionary with column statistics
        """
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        
        series = df[column]
        col_type = self.detect_column_type(series)
        
        summary = {
            'name': column,
            'type': col_type,
            'dtype': str(series.dtype),
            'count': len(series),
            'null_count': series.isna().sum(),
            'null_percentage': round(series.isna().sum() / len(series) * 100, 2),
            'unique_count': series.nunique(),
        }
        
        # Add type-specific statistics
        if col_type == 'numerical':
            summary.update({
                'min': float(series.min()) if not series.isna().all() else None,
                'max': float(series.max()) if not series.isna().all() else None,
                'mean': float(series.mean()) if not series.isna().all() else None,
                'median': float(series.median()) if not series.isna().all() else None,
                'std': float(series.std()) if not series.isna().all() else None,
                'q25': float(series.quantile(0.25)) if not series.isna().all() else None,
                'q75': float(series.quantile(0.75)) if not series.isna().all() else None,
            })
        elif col_type == 'categorical':
            value_counts = series.value_counts().head(10)
            summary.update({
                'top_values': value_counts.to_dict(),
                'most_common': str(series.mode().iloc[0]) if len(series.mode()) > 0 else None,
            })
        elif col_type == 'datetime':
            try:
                dt_series = pd.to_datetime(series, errors='coerce')
                summary.update({
                    'min_date': str(dt_series.min()) if not dt_series.isna().all() else None,
                    'max_date': str(dt_series.max()) if not dt_series.isna().all() else None,
                    'date_range_days': (dt_series.max() - dt_series.min()).days if not dt_series.isna().all() else None,
                })
            except:
                pass
        
        return summary
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the entire DataFrame.
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Dictionary containing dataset summary
        """
        type_info = self.analyze_data_types(df)
        
        # Categorize columns by type
        numerical_cols = [col for col, info in type_info.items() if info['semantic_type'] == 'numerical']
        categorical_cols = [col for col, info in type_info.items() if info['semantic_type'] == 'categorical']
        datetime_cols = [col for col, info in type_info.items() if info['semantic_type'] == 'datetime']
        text_cols = [col for col, info in type_info.items() if info['semantic_type'] == 'text']
        
        # Calculate missing values statistics
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isna().sum().sum()
        
        summary = {
            'shape': {
                'rows': df.shape[0],
                'columns': df.shape[1],
            },
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024**2), 2),
            'column_types': {
                'numerical': len(numerical_cols),
                'categorical': len(categorical_cols),
                'datetime': len(datetime_cols),
                'text': len(text_cols),
            },
            'columns_by_type': {
                'numerical': numerical_cols,
                'categorical': categorical_cols,
                'datetime': datetime_cols,
                'text': text_cols,
            },
            'missing_values': {
                'total_cells': total_cells,
                'missing_cells': missing_cells,
                'missing_percentage': round(missing_cells / total_cells * 100, 2) if total_cells > 0 else 0,
                'columns_with_missing': [
                    col for col, info in type_info.items() 
                    if info['null_count'] > 0
                ],
            },
            'column_details': type_info,
        }
        
        return summary
    
    def handle_missing_values(
        self, 
        df: pd.DataFrame, 
        strategy: str = 'auto',
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Handle missing values in the DataFrame.
        
        Args:
            df: DataFrame to process
            strategy: Strategy for handling missing values
                     'drop': Drop rows with missing values
                     'fill_mean': Fill with mean (numerical)
                     'fill_median': Fill with median (numerical)
                     'fill_mode': Fill with mode (categorical)
                     'auto': Auto-select strategy based on column type
            columns: Columns to process (all if None)
            
        Returns:
            DataFrame with missing values handled
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df.columns.tolist()
        
        for column in columns:
            if column not in df.columns:
                continue
            
            series = df_copy[column]
            
            if series.isna().sum() == 0:
                continue
            
            col_type = self.detect_column_type(series)
            
            if strategy == 'drop':
                df_copy = df_copy.dropna(subset=[column])
            elif strategy == 'auto':
                if col_type == 'numerical':
                    df_copy[column].fillna(series.median(), inplace=True)
                elif col_type == 'categorical':
                    df_copy[column].fillna(series.mode().iloc[0] if len(series.mode()) > 0 else 'Unknown', inplace=True)
            elif strategy == 'fill_mean' and col_type == 'numerical':
                df_copy[column].fillna(series.mean(), inplace=True)
            elif strategy == 'fill_median' and col_type == 'numerical':
                df_copy[column].fillna(series.median(), inplace=True)
            elif strategy == 'fill_mode':
                df_copy[column].fillna(series.mode().iloc[0] if len(series.mode()) > 0 else 'Unknown', inplace=True)
        
        return df_copy
    
    def smart_sample(
        self, 
        df: pd.DataFrame, 
        n: Optional[int] = None,
        strategy: str = 'random'
    ) -> pd.DataFrame:
        """
        Create a smart sample of the DataFrame for quick analysis.
        
        Args:
            df: DataFrame to sample
            n: Number of rows to sample (uses SAMPLE_SIZE if None)
            strategy: Sampling strategy ('random', 'first', 'stratified')
            
        Returns:
            Sampled DataFrame
        """
        if n is None:
            n = min(self.settings.SAMPLE_SIZE, len(df))
        
        if len(df) <= n:
            return df.copy()
        
        if strategy == 'random':
            return df.sample(n=n, random_state=42)
        elif strategy == 'first':
            return df.head(n)
        elif strategy == 'stratified':
            # Try to stratify by first categorical column
            type_info = self.analyze_data_types(df)
            categorical_cols = [col for col, info in type_info.items() if info['semantic_type'] == 'categorical']
            
            if categorical_cols:
                # Stratified sampling on first categorical column
                stratify_col = categorical_cols[0]
                return df.groupby(stratify_col, group_keys=False).apply(
                    lambda x: x.sample(min(len(x), max(1, n // df[stratify_col].nunique())), random_state=42)
                ).head(n)
            else:
                # Fallback to random
                return df.sample(n=n, random_state=42)
        
        return df.sample(n=n, random_state=42)
    
    def convert_to_appropriate_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert DataFrame columns to most appropriate data types for analysis.
        
        Args:
            df: DataFrame to convert
            
        Returns:
            DataFrame with optimized types
        """
        df_copy = df.copy()
        type_info = self.analyze_data_types(df)
        
        for column, info in type_info.items():
            semantic_type = info['semantic_type']
            
            try:
                if semantic_type == 'datetime':
                    df_copy[column] = pd.to_datetime(df_copy[column], errors='coerce')
                elif semantic_type == 'categorical':
                    df_copy[column] = df_copy[column].astype('category')
                elif semantic_type == 'numerical':
                    # Try to convert to numeric if not already
                    if not pd.api.types.is_numeric_dtype(df_copy[column]):
                        df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce')
            except Exception:
                # Keep original type if conversion fails
                pass
        
        return df_copy
