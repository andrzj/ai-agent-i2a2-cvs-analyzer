"""
Unit Tests for CSV Analyzer AI Agent

Test suite for core functionality.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.csv_loader import CSVLoader
from utils.data_processor import DataProcessor


class TestCSVLoader:
    """Tests for CSV Loader."""
    
    def test_detect_encoding(self):
        """Test encoding detection."""
        # This test would need actual CSV files
        pass
    
    def test_validate_file(self):
        """Test file validation."""
        loader = CSVLoader()
        # Test with non-existent file
        is_valid, error = loader.validate_file("/nonexistent/file.csv")
        assert not is_valid
        assert "not found" in error.lower()


class TestDataProcessor:
    """Tests for Data Processor."""
    
    def test_detect_column_type_numerical(self):
        """Test numerical column detection."""
        processor = DataProcessor()
        
        # Create test series
        series = pd.Series([1, 2, 3, 4, 5])
        col_type = processor.detect_column_type(series)
        
        assert col_type == 'numerical'
    
    def test_detect_column_type_categorical(self):
        """Test categorical column detection."""
        processor = DataProcessor()
        
        # Create test series
        series = pd.Series(['A', 'B', 'C', 'A', 'B'])
        col_type = processor.detect_column_type(series)
        
        assert col_type == 'categorical'
    
    def test_get_data_summary(self):
        """Test data summary generation."""
        processor = DataProcessor()
        
        # Create test DataFrame
        df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'salary': [50000, 60000, 70000, 80000, 90000]
        })
        
        summary = processor.get_data_summary(df)
        
        assert summary['shape']['rows'] == 5
        assert summary['shape']['columns'] == 3
        assert 'numerical' in summary['column_types']
        assert 'categorical' in summary['column_types']
    
    def test_handle_missing_values(self):
        """Test missing value handling."""
        processor = DataProcessor()
        
        # Create DataFrame with missing values
        df = pd.DataFrame({
            'col1': [1, 2, np.nan, 4, 5],
            'col2': ['A', 'B', None, 'D', 'E']
        })
        
        # Fill with auto strategy
        df_filled = processor.handle_missing_values(df, strategy='auto')
        
        assert df_filled['col1'].isna().sum() == 0
        assert df_filled['col2'].isna().sum() == 0
    
    def test_smart_sample(self):
        """Test smart sampling."""
        processor = DataProcessor()
        
        # Create large DataFrame
        df = pd.DataFrame({
            'col1': range(1000),
            'col2': ['A'] * 500 + ['B'] * 500
        })
        
        # Sample
        df_sample = processor.smart_sample(df, n=100, strategy='random')
        
        assert len(df_sample) == 100
        assert set(df_sample.columns) == {'col1', 'col2'}


class TestTools:
    """Tests for analysis tools."""
    
    def test_data_description_tools(self):
        """Test data description tools."""
        # Would need to set up DataFrame and test each tool
        pass
    
    def test_pattern_analysis_tools(self):
        """Test pattern analysis tools."""
        pass
    
    def test_outlier_detection_tools(self):
        """Test outlier detection tools."""
        pass
    
    def test_relationship_analysis_tools(self):
        """Test relationship analysis tools."""
        pass
    
    def test_visualization_tools(self):
        """Test visualization tools."""
        pass


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
