"""
CSV Agent Module

Main agent implementation for CSV analysis using LangChain.
"""

import pandas as pd
import json
import logging
from typing import Dict, Any, Optional, List
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.callbacks.base import BaseCallbackHandler

logger = logging.getLogger(__name__)


class VisualizationCallbackHandler(BaseCallbackHandler):
    """Callback handler to capture tool outputs containing visualizations."""
    
    def __init__(self):
        self.tool_outputs = []
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool finishes execution."""
        if 'PLOT_JSON:' in output:
            logger.info(f"Callback captured tool output with PLOT_JSON, length: {len(output)}")
            self.tool_outputs.append(output)
    
    def reset(self):
        """Reset captured outputs."""
        self.tool_outputs = []

from config.settings import Settings
from utils import DataProcessor
from .memory import AnalysisMemory

# Import all tools
from tools.data_description import (
    get_data_types_tool, get_distribution_stats_tool, get_range_info_tool,
    calculate_central_tendency_tool, calculate_variability_tool,
    set_dataframe as set_df_description
)
from tools.pattern_analysis import (
    detect_temporal_patterns_tool, get_frequency_analysis_tool,
    detect_clusters_tool
)
from tools.outlier_detection import (
    detect_outliers_iqr_tool, detect_outliers_zscore_tool,
    analyze_outlier_impact_tool, detect_all_outliers_tool
)
from tools.relationship_analysis import (
    calculate_correlation_tool, analyze_variable_relationships_tool,
    identify_influential_variables_tool
)
from tools.visualization import (
    create_histogram_tool, create_scatter_plot_tool,
    create_correlation_heatmap_tool, create_box_plot_tool,
    create_time_series_plot_tool
)


class CSVAgent:
    """
    AI Agent for CSV data analysis.
    
    Uses LangChain with custom tools to analyze CSV data and answer questions.
    LLM is used ONLY for intent understanding and tool selection, never for
    processing raw CSV data.
    """
    
    def __init__(self, llm_model: Optional[str] = None, temperature: Optional[float] = None, api_key: Optional[str] = None):
        """
        Initialize the CSV Agent.
        
        Args:
            llm_model: LLM model name (uses Settings default if None)
            temperature: LLM temperature (uses Settings default if None)
            api_key: OpenAI API key (uses Settings default if None)
        """
        self.settings = Settings
        self.data_processor = DataProcessor()
        self.memory = AnalysisMemory()
        
        # Initialize LLM
        self.llm_model = llm_model or self.settings.LLM_MODEL
        self.temperature = temperature if temperature is not None else self.settings.LLM_TEMPERATURE
        
        # Use provided API key or fall back to settings
        self.api_key = api_key or self.settings.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please provide it via parameter or configure in settings.")
        
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=self.temperature,
            openai_api_key=self.api_key
        )
        
        # DataFrame and agent will be set when data is loaded
        self.df: Optional[pd.DataFrame] = None
        self.agent = None
        self.agent_executor = None
        
        # Callback handler to capture visualization outputs
        self.viz_callback = VisualizationCallbackHandler()
        
        # Dataset metadata
        self.dataset_info: Optional[Dict[str, Any]] = None
    
    def load_dataframe(self, df: pd.DataFrame, dataset_info: Optional[Dict[str, Any]] = None):
        """
        Load a DataFrame for analysis.
        
        Args:
            df: Pandas DataFrame to analyze
            dataset_info: Optional metadata about the dataset
        """
        self.df = df
        self.dataset_info = dataset_info or {}
        
        # Set DataFrame for all tools
        set_df_description(df, self.data_processor)
        
        # Get data summary
        data_summary = self.data_processor.get_data_summary(df)
        self.memory.set_dataset_summary(data_summary)
        
        # Initialize agent with tools
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LangChain agent with all tools."""
        if self.df is None:
            raise ValueError("DataFrame not loaded. Call load_dataframe() first.")
        
        # Collect all tools
        tools = [
            # Data Description (5 tools)
            get_data_types_tool,
            get_distribution_stats_tool,
            get_range_info_tool,
            calculate_central_tendency_tool,
            calculate_variability_tool,
            # Pattern Analysis (3 tools)
            detect_temporal_patterns_tool,
            get_frequency_analysis_tool,
            detect_clusters_tool,
            # Outlier Detection (4 tools)
            detect_all_outliers_tool,  # New tool for detecting outliers across all columns
            detect_outliers_iqr_tool,
            detect_outliers_zscore_tool,
            analyze_outlier_impact_tool,
            # Relationship Analysis (3 tools)
            calculate_correlation_tool,
            analyze_variable_relationships_tool,
            identify_influential_variables_tool,
            # Visualization (5 tools)
            create_histogram_tool,
            create_scatter_plot_tool,
            create_correlation_heatmap_tool,
            create_box_plot_tool,
            create_time_series_plot_tool,
        ]
        
        # Create system prompt with dataset info
        data_summary = self.memory.dataset_summary
        
        column_info = ""
        if data_summary:
            for col_type, cols in data_summary.get('columns_by_type', {}).items():
                if cols:
                    column_info += f"\n  • {col_type.upper()}: {', '.join(cols[:10])}"
                    if len(cols) > 10:
                        column_info += f" ... and {len(cols) - 10} more"
        
        system_prompt = self.settings.SYSTEM_PROMPT_TEMPLATE.format(
            num_rows=data_summary.get('shape', {}).get('rows', 'Unknown') if data_summary else 'Unknown',
            num_columns=data_summary.get('shape', {}).get('columns', 'Unknown') if data_summary else 'Unknown',
            column_info=column_info or "No column information available"
        )
        
        # Initialize agent
        self.agent_executor = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=self.settings.AGENT_VERBOSE,
            memory=self.memory.conversation_memory,
            max_iterations=self.settings.MAX_AGENT_ITERATIONS,
            early_stopping_method="generate",
            handle_parsing_errors=True,
            agent_kwargs={
                "system_message": system_prompt,
                "prefix": system_prompt
            }
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Ask a question about the data.
        
        Args:
            question: Natural language question about the data
            
        Returns:
            Dictionary containing:
                - answer: The agent's response
                - visualizations: List of visualization JSONs (if any)
                - metadata: Additional metadata about the response
        """
        if self.agent_executor is None:
            raise ValueError("Agent not initialized. Load data first with load_dataframe().")
        
        try:
            # Reset callback handler
            self.viz_callback.reset()
            
            # Run the agent with callback
            response = self.agent_executor.invoke(
                {"input": question},
                config={"callbacks": [self.viz_callback]}
            )
            
            # Extract output
            output = response.get('output', '')
            logger.info(f"Agent output length: {len(output)} chars")
            logger.info(f"Callback captured {len(self.viz_callback.tool_outputs)} tool outputs with PLOT_JSON")
            
            # Extract visualizations from callback-captured tool outputs
            visualizations = []
            
            # Process each tool output captured by callback
            for tool_output in self.viz_callback.tool_outputs:
                logger.info(f"Processing tool output, length: {len(tool_output)} chars")
                
                if 'PLOT_JSON:' in tool_output:
                    # Extract visualization JSONs from tool output
                    parts = tool_output.split('PLOT_JSON:')
                    
                    for i in range(1, len(parts)):
                        viz_part = parts[i].strip()
                        if viz_part:
                            # Try to extract just the JSON part
                            # JSON objects start with { and end with }, arrays with [ and ]
                            try:
                                # Attempt to parse and validate it's proper JSON
                                if viz_part.startswith('{'):
                                    # Find the matching closing brace
                                    brace_count = 0
                                    end_idx = 0
                                    for idx, char in enumerate(viz_part):
                                        if char == '{':
                                            brace_count += 1
                                        elif char == '}':
                                            brace_count -= 1
                                            if brace_count == 0:
                                                end_idx = idx + 1
                                                break
                                    if end_idx > 0:
                                        viz_json = viz_part[:end_idx]
                                        # Validate it's proper JSON
                                        json.loads(viz_json)
                                        visualizations.append(viz_json)
                                        logger.info(f"Extracted visualization JSON, length: {len(viz_json)} chars")
                                elif viz_part.startswith('['):
                                    # Similar logic for arrays
                                    bracket_count = 0
                                    end_idx = 0
                                    for idx, char in enumerate(viz_part):
                                        if char == '[':
                                            bracket_count += 1
                                        elif char == ']':
                                            bracket_count -= 1
                                            if bracket_count == 0:
                                                end_idx = idx + 1
                                                break
                                    if end_idx > 0:
                                        viz_json = viz_part[:end_idx]
                                        # Validate it's proper JSON
                                        json.loads(viz_json)
                                        visualizations.append(viz_json)
                                        logger.info(f"Extracted visualization JSON, length: {len(viz_json)} chars")
                            except (json.JSONDecodeError, ValueError) as e:
                                # Skip invalid JSON
                                logger.warning(f"Skipping invalid visualization JSON: {str(e)}")
                                pass
            
            logger.info(f"Total visualizations extracted: {len(visualizations)}")
            
            # Record in memory
            self.memory.add_conversation_turn(question, output)
            
            return {
                'answer': output,
                'visualizations': visualizations,
                'metadata': {
                    'question': question,
                    'context_summary': self.memory.get_context_summary()
                }
            }
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            return {
                'answer': error_msg,
                'visualizations': [],
                'metadata': {'error': str(e)}
            }
    
    def get_dataset_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary of the loaded dataset."""
        return self.memory.dataset_summary
    
    def get_conversation_history(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Args:
            last_n: Number of recent messages to retrieve
            
        Returns:
            List of conversation turns with 'human' and 'ai' keys
        """
        messages = self.memory.get_conversation_history(last_n)
        
        history = []
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    'human': messages[i].content,
                    'ai': messages[i + 1].content
                })
        
        return history
    
    def get_analysis_history(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get history of analyses performed."""
        return self.memory.get_analysis_history(last_n=last_n)
    
    def reset_memory(self):
        """Clear conversation and analysis history."""
        self.memory.clear()
        
        if self.df is not None:
            # Reinitialize with current data
            data_summary = self.data_processor.get_data_summary(self.df)
            self.memory.set_dataset_summary(data_summary)
    
    def export_session(self) -> Dict[str, Any]:
        """
        Export the current session (memory, data info, etc.).
        
        Returns:
            Dictionary containing session state
        """
        return {
            'dataset_info': self.dataset_info,
            'memory': self.memory.export_history(),
            'llm_model': self.llm_model,
            'temperature': self.temperature
        }
    
    def import_session(self, session_data: Dict[str, Any]):
        """
        Import a previously exported session.
        
        Args:
            session_data: Session data from export_session()
        """
        self.dataset_info = session_data.get('dataset_info', {})
        self.memory.import_history(session_data.get('memory', {}))
