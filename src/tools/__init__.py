"""Tools package for CSV Analyzer AI Agent."""

# Import all tools for easy access
from .data_description import (
    get_data_types_tool,
    get_distribution_stats_tool,
    get_range_info_tool,
    calculate_central_tendency_tool,
    calculate_variability_tool,
)

from .pattern_analysis import (
    detect_temporal_patterns_tool,
    get_frequency_analysis_tool,
    detect_clusters_tool,
)

from .outlier_detection import (
    detect_outliers_iqr_tool,
    detect_outliers_zscore_tool,
    analyze_outlier_impact_tool,
)

from .relationship_analysis import (
    calculate_correlation_tool,
    analyze_variable_relationships_tool,
    identify_influential_variables_tool,
)

from .visualization import (
    create_histogram_tool,
    create_scatter_plot_tool,
    create_correlation_heatmap_tool,
    create_box_plot_tool,
    create_time_series_plot_tool,
)

__all__ = [
    # Data Description
    "get_data_types_tool",
    "get_distribution_stats_tool",
    "get_range_info_tool",
    "calculate_central_tendency_tool",
    "calculate_variability_tool",
    # Pattern Analysis
    "detect_temporal_patterns_tool",
    "get_frequency_analysis_tool",
    "detect_clusters_tool",
    # Outlier Detection
    "detect_outliers_iqr_tool",
    "detect_outliers_zscore_tool",
    "analyze_outlier_impact_tool",
    # Relationship Analysis
    "calculate_correlation_tool",
    "analyze_variable_relationships_tool",
    "identify_influential_variables_tool",
    # Visualization
    "create_histogram_tool",
    "create_scatter_plot_tool",
    "create_correlation_heatmap_tool",
    "create_box_plot_tool",
    "create_time_series_plot_tool",
]
