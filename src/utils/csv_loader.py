"""
CSV Loader Module

Handles loading and validation of CSV files, including support for large files,
multiple encodings, and chunked reading for memory efficiency.
"""

import os
import io
import chardet
import pandas as pd
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from config.settings import Settings


class CSVLoader:
    """
    Utility class for loading and validating CSV files.
    
    Supports:
    - Large file handling with chunked reading
    - Multiple encoding detection
    - CSV structure validation
    - File statistics calculation
    """
    
    def __init__(self):
        """Initialize CSV Loader."""
        self.settings = Settings
        
    def detect_encoding(self, file_path: str, sample_size: int = 100000) -> str:
        """
        Detect the encoding of a CSV file.
        
        Args:
            file_path: Path to the CSV file
            sample_size: Number of bytes to sample for detection
            
        Returns:
            Detected encoding name
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read(sample_size)
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            
            # Fallback to UTF-8 if detection fails
            if encoding is None:
                encoding = 'utf-8'
                
        return encoding
    
    def validate_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that the file exists, is readable, and within size limits.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return False, f"File is not readable: {file_path}"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > self.settings.MAX_FILE_SIZE_BYTES:
            return False, (
                f"File size ({file_size / (1024**2):.2f} MB) exceeds "
                f"maximum allowed size ({self.settings.MAX_FILE_SIZE_MB} MB)"
            )
        
        # Check file extension
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        if file_ext not in self.settings.SUPPORTED_FILE_TYPES:
            return False, (
                f"Unsupported file type: {file_ext}. "
                f"Supported types: {', '.join(self.settings.SUPPORTED_FILE_TYPES)}"
            )
        
        return True, None
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic statistics about the CSV file without loading it entirely.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary containing file statistics
        """
        file_size = os.path.getsize(file_path)
        encoding = self.detect_encoding(file_path)
        
        # Count lines quickly
        with open(file_path, 'r', encoding=encoding) as f:
            # Read first line to get column count
            first_line = f.readline()
            num_columns = len(first_line.split(','))
            
            # Count total lines (including header)
            num_lines = 1 + sum(1 for _ in f)
        
        return {
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024**2), 2),
            'encoding': encoding,
            'num_rows': num_lines - 1,  # Exclude header
            'num_columns': num_columns,
            'estimated_memory_mb': round((file_size * 2.5) / (1024**2), 2)  # Rough estimate
        }
    
    def load_csv(
        self, 
        file_path: str, 
        encoding: Optional[str] = None,
        use_chunking: bool = False,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load a CSV file into a pandas DataFrame.
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding (auto-detected if None)
            use_chunking: Whether to use chunked reading for large files
            **kwargs: Additional arguments to pass to pd.read_csv
            
        Returns:
            Loaded DataFrame
            
        Raises:
            ValueError: If file validation fails
            pd.errors.ParserError: If CSV parsing fails
        """
        # Validate file
        is_valid, error_msg = self.validate_file(file_path)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Detect encoding if not provided
        if encoding is None:
            encoding = self.detect_encoding(file_path)
        
        try:
            # Try with detected encoding first
            df = self._load_with_encoding(file_path, encoding, use_chunking, **kwargs)
            return df
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            # Try alternative encodings
            for alt_encoding in self.settings.SUPPORTED_ENCODINGS:
                if alt_encoding == encoding:
                    continue
                try:
                    df = self._load_with_encoding(file_path, alt_encoding, use_chunking, **kwargs)
                    return df
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            
            # If all encodings fail, raise the original error
            raise ValueError(f"Failed to load CSV with any supported encoding. Original error: {str(e)}")
    
    def _load_with_encoding(
        self, 
        file_path: str, 
        encoding: str,
        use_chunking: bool = False,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load CSV with a specific encoding.
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding
            use_chunking: Whether to use chunked reading
            **kwargs: Additional arguments to pass to pd.read_csv
            
        Returns:
            Loaded DataFrame
        """
        if use_chunking:
            # Load in chunks for large files
            chunks = []
            chunk_iterator = pd.read_csv(
                file_path,
                encoding=encoding,
                chunksize=self.settings.CSV_CHUNK_SIZE,
                **kwargs
            )
            for chunk in chunk_iterator:
                chunks.append(chunk)
            df = pd.concat(chunks, ignore_index=True)
        else:
            # Load entire file at once
            df = pd.read_csv(file_path, encoding=encoding, **kwargs)
        
        return df
    
    def load_sample(
        self, 
        file_path: str, 
        n_rows: Optional[int] = None,
        encoding: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load a sample of rows from a CSV file for quick exploration.
        
        Args:
            file_path: Path to the CSV file
            n_rows: Number of rows to sample (uses SAMPLE_SIZE if None)
            encoding: File encoding (auto-detected if None)
            **kwargs: Additional arguments to pass to pd.read_csv
            
        Returns:
            Sample DataFrame
        """
        if n_rows is None:
            n_rows = self.settings.SAMPLE_SIZE
        
        if encoding is None:
            encoding = self.detect_encoding(file_path)
        
        try:
            df = pd.read_csv(file_path, encoding=encoding, nrows=n_rows, **kwargs)
            return df
        except (UnicodeDecodeError, pd.errors.ParserError):
            # Try alternative encodings
            for alt_encoding in self.settings.SUPPORTED_ENCODINGS:
                if alt_encoding == encoding:
                    continue
                try:
                    df = pd.read_csv(file_path, encoding=alt_encoding, nrows=n_rows, **kwargs)
                    return df
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            
            raise ValueError("Failed to load CSV sample with any supported encoding")
    
    def smart_load(self, file_path: str, **kwargs) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Intelligently load a CSV file, choosing the best strategy based on file size.
        
        Args:
            file_path: Path to the CSV file
            **kwargs: Additional arguments to pass to pd.read_csv
            
        Returns:
            Tuple of (DataFrame, file_stats)
        """
        # Get file statistics
        stats = self.get_file_stats(file_path)
        
        # Decide loading strategy based on file size
        use_chunking = stats['file_size_mb'] > 50  # Use chunking for files > 50 MB
        
        # Load the file
        df = self.load_csv(file_path, use_chunking=use_chunking, **kwargs)
        
        # Update stats with actual loaded data
        stats['num_rows'] = len(df)
        stats['num_columns'] = len(df.columns)
        stats['column_names'] = df.columns.tolist()
        stats['actual_memory_mb'] = round(df.memory_usage(deep=True).sum() / (1024**2), 2)
        
        return df, stats
