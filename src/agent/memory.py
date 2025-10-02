"""
Analysis Memory Module

Manages conversation history and analysis results for the CSV Analyzer AI Agent.
Provides context-aware memory that remembers previous analyses and conclusions.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from config.settings import Settings


class AnalysisMemory:
    """
    Memory system for storing and retrieving conversation history and analysis results.
    
    Features:
    - Conversation buffer memory
    - Analysis history tracking
    - Automatic summarization when threshold reached
    - Context retrieval for follow-up questions
    """
    
    def __init__(self):
        """Initialize the analysis memory system."""
        self.settings = Settings
        
        # Conversation memory
        self.conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Analysis history (stores metadata about analyses performed)
        self.analysis_history: List[Dict[str, Any]] = []
        
        # Conclusions drawn from analyses
        self.conclusions: List[Dict[str, Any]] = []
        
        # Dataset summary (set when data is loaded)
        self.dataset_summary: Optional[Dict[str, Any]] = None
    
    def set_dataset_summary(self, summary: Dict[str, Any]):
        """
        Set the dataset summary information.
        
        Args:
            summary: Dictionary containing dataset metadata
        """
        self.dataset_summary = summary
    
    def add_conversation_turn(self, human_input: str, ai_response: str):
        """
        Add a conversation turn to memory.
        
        Args:
            human_input: User's question/input
            ai_response: Agent's response
        """
        self.conversation_memory.chat_memory.add_user_message(human_input)
        self.conversation_memory.chat_memory.add_ai_message(ai_response)
        
        # Check if we need to summarize
        if len(self.conversation_memory.chat_memory.messages) > self.settings.MEMORY_SUMMARY_THRESHOLD:
            self._summarize_old_conversations()
    
    def add_analysis_result(
        self,
        analysis_type: str,
        tool_used: str,
        inputs: Dict[str, Any],
        outputs: Any,
        timestamp: Optional[datetime] = None
    ):
        """
        Record an analysis that was performed.
        
        Args:
            analysis_type: Type of analysis (e.g., 'correlation', 'outlier_detection')
            tool_used: Name of the tool that was used
            inputs: Input parameters to the tool
            outputs: Results/outputs from the tool
            timestamp: When the analysis was performed (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        analysis_record = {
            'timestamp': timestamp.isoformat(),
            'analysis_type': analysis_type,
            'tool_used': tool_used,
            'inputs': inputs,
            'outputs_summary': str(outputs)[:500],  # Store summary to avoid memory bloat
        }
        
        self.analysis_history.append(analysis_record)
        
        # Keep only recent history
        if len(self.analysis_history) > self.settings.MAX_ANALYSIS_HISTORY:
            self.analysis_history = self.analysis_history[-self.settings.MAX_ANALYSIS_HISTORY:]
    
    def add_conclusion(self, conclusion: str, evidence: List[str]):
        """
        Record a conclusion drawn from analysis.
        
        Args:
            conclusion: The conclusion text
            evidence: List of supporting evidence/analyses
        """
        self.conclusions.append({
            'timestamp': datetime.now().isoformat(),
            'conclusion': conclusion,
            'evidence': evidence
        })
    
    def get_conversation_history(self, last_n: Optional[int] = None) -> List[BaseMessage]:
        """
        Get conversation history.
        
        Args:
            last_n: Number of recent messages to retrieve (all if None)
            
        Returns:
            List of conversation messages
        """
        messages = self.conversation_memory.chat_memory.messages
        
        if last_n is not None:
            return messages[-last_n:]
        
        return messages
    
    def get_analysis_history(
        self,
        analysis_type: Optional[str] = None,
        last_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get analysis history.
        
        Args:
            analysis_type: Filter by analysis type (all if None)
            last_n: Number of recent analyses to retrieve (all if None)
            
        Returns:
            List of analysis records
        """
        history = self.analysis_history
        
        if analysis_type:
            history = [a for a in history if a['analysis_type'] == analysis_type]
        
        if last_n is not None:
            return history[-last_n:]
        
        return history
    
    def get_conclusions(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recorded conclusions.
        
        Args:
            last_n: Number of recent conclusions to retrieve (all if None)
            
        Returns:
            List of conclusion records
        """
        if last_n is not None:
            return self.conclusions[-last_n:]
        
        return self.conclusions
    
    def get_context_summary(self) -> str:
        """
        Get a summary of the current context for the agent.
        
        Returns:
            String summarizing what has been analyzed so far
        """
        summary_parts = []
        
        # Dataset info
        if self.dataset_summary:
            summary_parts.append(
                f"Dataset: {self.dataset_summary.get('num_rows', 'Unknown')} rows, "
                f"{self.dataset_summary.get('num_columns', 'Unknown')} columns"
            )
        
        # Recent analyses
        if self.analysis_history:
            recent_analyses = self.analysis_history[-5:]
            analysis_types = list(set([a['analysis_type'] for a in recent_analyses]))
            summary_parts.append(
                f"Recent analyses: {', '.join(analysis_types)}"
            )
        
        # Conclusions
        if self.conclusions:
            summary_parts.append(
                f"{len(self.conclusions)} conclusions drawn"
            )
        
        if not summary_parts:
            return "No previous context available."
        
        return " | ".join(summary_parts)
    
    def search_relevant_history(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for relevant previous analyses based on a query.
        
        Args:
            query: Search query (column names, analysis types, etc.)
            
        Returns:
            List of relevant analysis records
        """
        query_lower = query.lower()
        relevant = []
        
        for analysis in self.analysis_history:
            # Check if query matches tool name, inputs, or analysis type
            if (query_lower in analysis['tool_used'].lower() or
                query_lower in analysis['analysis_type'].lower() or
                query_lower in str(analysis['inputs']).lower()):
                relevant.append(analysis)
        
        return relevant
    
    def _summarize_old_conversations(self):
        """
        Summarize old conversations to reduce memory size.
        This is called automatically when conversation history gets too long.
        """
        messages = self.conversation_memory.chat_memory.messages
        
        if len(messages) > self.settings.MEMORY_SUMMARY_THRESHOLD * 2:
            # Keep only recent messages
            self.conversation_memory.chat_memory.messages = messages[
                -self.settings.MAX_CONVERSATION_HISTORY:
            ]
    
    def clear(self):
        """Clear all memory."""
        self.conversation_memory.clear()
        self.analysis_history.clear()
        self.conclusions.clear()
        self.dataset_summary = None
    
    def export_history(self) -> Dict[str, Any]:
        """
        Export all memory as JSON-serializable dictionary.
        
        Returns:
            Dictionary containing all memory state
        """
        return {
            'dataset_summary': self.dataset_summary,
            'conversation_history': [
                {'type': type(msg).__name__, 'content': msg.content}
                for msg in self.conversation_memory.chat_memory.messages
            ],
            'analysis_history': self.analysis_history,
            'conclusions': self.conclusions
        }
    
    def import_history(self, history_dict: Dict[str, Any]):
        """
        Import memory state from dictionary.
        
        Args:
            history_dict: Dictionary containing memory state
        """
        self.dataset_summary = history_dict.get('dataset_summary')
        self.analysis_history = history_dict.get('analysis_history', [])
        self.conclusions = history_dict.get('conclusions', [])
        
        # Reconstruct conversation messages
        self.conversation_memory.chat_memory.clear()
        for msg_dict in history_dict.get('conversation_history', []):
            if msg_dict['type'] == 'HumanMessage':
                self.conversation_memory.chat_memory.add_user_message(msg_dict['content'])
            elif msg_dict['type'] == 'AIMessage':
                self.conversation_memory.chat_memory.add_ai_message(msg_dict['content'])
