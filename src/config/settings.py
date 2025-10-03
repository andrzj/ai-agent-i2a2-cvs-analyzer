"""
Configuration settings for CSV Analyzer AI Agent.

This module contains all configuration constants and settings used throughout the application.
"""

import os
import re
from typing import Final, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings and configuration constants."""
    
    # ============================================================
    # LLM Configuration
    # ============================================================
    OPENAI_API_KEY: Final[str] = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: Final[str] = os.getenv("ANTHROPIC_API_KEY", "")
    
    LLM_MODEL: Final[str] = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    LLM_TEMPERATURE: Final[float] = float(os.getenv("LLM_TEMPERATURE", "0"))
    
    # ============================================================
    # File Processing Configuration
    # ============================================================
    MAX_FILE_SIZE_MB: Final[int] = int(os.getenv("MAX_FILE_SIZE_MB", "200"))
    MAX_FILE_SIZE_BYTES: Final[int] = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Chunk size for reading large CSV files
    CSV_CHUNK_SIZE: Final[int] = 50000  # rows per chunk
    
    # Supported file types
    SUPPORTED_FILE_TYPES: Final[List[str]] = ["csv"]
    
    # Encoding detection
    SUPPORTED_ENCODINGS: Final[List[str]] = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
    
    # ============================================================
    # Data Processing Configuration
    # ============================================================
    # Threshold for categorical vs numerical detection
    CATEGORICAL_THRESHOLD: Final[int] = 50  # Max unique values for categorical
    
    # Sample size for quick exploratory analysis
    SAMPLE_SIZE: Final[int] = 10000  # rows
    
    # Missing value threshold (percentage)
    MISSING_VALUE_WARNING_THRESHOLD: Final[float] = 0.3  # 30%
    
    # ============================================================
    # Statistical Analysis Configuration
    # ============================================================
    # Outlier detection
    IQR_MULTIPLIER: Final[float] = 1.5
    ZSCORE_THRESHOLD: Final[float] = 3.0
    
    # Correlation thresholds
    CORRELATION_WEAK_THRESHOLD: Final[float] = 0.3
    CORRELATION_MODERATE_THRESHOLD: Final[float] = 0.5
    CORRELATION_STRONG_THRESHOLD: Final[float] = 0.7
    
    # Clustering
    DEFAULT_N_CLUSTERS: Final[int] = 3
    MAX_CLUSTERS: Final[int] = 10
    
    # ============================================================
    # Memory Configuration
    # ============================================================
    MAX_CONVERSATION_HISTORY: Final[int] = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
    MEMORY_SUMMARY_THRESHOLD: Final[int] = int(os.getenv("MEMORY_SUMMARY_THRESHOLD", "20"))
    
    # Store analysis results in memory
    ENABLE_ANALYSIS_HISTORY: Final[bool] = True
    MAX_ANALYSIS_HISTORY: Final[int] = 100
    
    # ============================================================
    # Visualization Configuration
    # ============================================================
    # Default plot dimensions
    DEFAULT_PLOT_WIDTH: Final[int] = 800
    DEFAULT_PLOT_HEIGHT: Final[int] = 600
    
    # Color schemes
    DEFAULT_COLOR_SCHEME: Final[str] = "viridis"
    CATEGORICAL_COLORS: Final[List[str]] = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]
    
    # Maximum categories to display in charts
    MAX_CATEGORIES_DISPLAY: Final[int] = 20
    
    # Histogram bins
    DEFAULT_HISTOGRAM_BINS: Final[int] = 30
    
    # ============================================================
    # Agent Configuration
    # ============================================================
    # Agent type
    AGENT_TYPE: Final[str] = "CONVERSATIONAL_REACT_DESCRIPTION"
    
    # Maximum iterations for agent reasoning
    MAX_AGENT_ITERATIONS: Final[int] = 10
    
    # Verbose mode for debugging
    AGENT_VERBOSE: Final[bool] = True  # Temporarily enabled to debug visualization issue
    
    # System prompt template
    SYSTEM_PROMPT_TEMPLATE: Final[str] = """Você é um agente de IA especialista em análise de dados, especializado em análise de dados CSV.

Você tem acesso a um arquivo CSV com {num_rows} linhas e {num_columns} colunas.

Informações das Colunas:
{column_info}

REGRAS CRÍTICAS:
1. NUNCA envie dados CSV para seu contexto - sempre use as ferramentas fornecidas
2. Use ferramentas para analisar dados e obter insights
3. Forneça insights claros e acionáveis baseados nas saídas das ferramentas
4. Quando apropriado, gere visualizações para melhorar o entendimento
5. Lembre-se de análises anteriores e construa sobre elas
6. Se uma pergunta for ambígua, peça esclarecimento
7. Explique conceitos estatísticos em termos simples

Ferramentas Disponíveis:
Você tem acesso a 20 ferramentas especializadas para:
- Descrição de dados (tipos, distribuições, intervalos, estatísticas)
- Análise de padrões (tendências temporais, frequência, clustering)
- Detecção de outliers (IQR, Z-score, análise de impacto)
- Análise de relacionamentos (correlação, dependências, influência)
- Visualização (histogramas, gráficos de dispersão, mapas de calor, box plots, séries temporais)

Seu objetivo é ajudar os usuários a entender seus dados através de análise cuidadosa e explicações claras.
Utilize a ferramenta de Visualização e adicione uma visualização à resposta sempre que ela puder ajudar a ilustrar seus pontos.

Sempre responda em Português Brasileiro
"""
    
    # ============================================================
    # Caching Configuration
    # ============================================================
    ENABLE_CACHING: Final[bool] = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL_SECONDS: Final[int] = 3600  # 1 hour
    
    # ============================================================
    # Logging Configuration
    # ============================================================
    LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ============================================================
    # UI Configuration
    # ============================================================
    APP_TITLE: Final[str] = "CSV Analyzer AI Agent 📊🤖"
    APP_ICON: Final[str] = "📊"
    
    # Suggested questions
    SUGGESTED_QUESTIONS: Final[List[str]] = [
        "Quais são os tipos de dados de cada coluna?",
        "Mostre-me a distribuição das colunas numéricas",
        "Existem outliers nos dados?",
        "Qual é a correlação entre as variáveis?",
        "Você pode identificar algum padrão ou tendência?",
        "Quais variáveis são mais influentes?",
    ]
    
    @classmethod
    def has_configured_api_key(cls) -> bool:
        """
        Check if an API key is configured in environment or .env file.
        
        Returns:
            True if OPENAI_API_KEY or ANTHROPIC_API_KEY is configured, False otherwise
        """
        return bool(cls.OPENAI_API_KEY or cls.ANTHROPIC_API_KEY)
    
    @classmethod
    def validate_api_key_format(cls, api_key: str) -> tuple[bool, Optional[str]]:
        """
        Validate the format of an OpenAI API key.
        
        Args:
            api_key: API key string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key or not api_key.strip():
            return False, "API key cannot be empty"
        
        api_key = api_key.strip()
        
        # OpenAI keys start with 'sk-' or 'sk-proj-' followed by alphanumeric characters
        if not re.match(r'^sk-[a-zA-Z0-9_-]{32,}$', api_key):
            return False, "Invalid API key format. OpenAI keys start with 'sk-' followed by at least 32 alphanumeric characters"
        
        return True, None
    
    @classmethod
    def mask_api_key(cls, api_key: str) -> str:
        """
        Mask an API key for safe display/logging.
        
        Args:
            api_key: API key to mask
            
        Returns:
            Masked API key showing only first 7 and last 4 characters
        """
        if not api_key or len(api_key) < 11:
            return "***"
        return f"{api_key[:7]}...{api_key[-4:]}"
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required settings are properly configured.
        Note: This is now optional - API key can be provided at runtime.
        
        Returns:
            True if validation passes, False otherwise
        """
        # Don't raise an error - just return False if no key is configured
        return cls.has_configured_api_key()


# Note: We no longer validate on import to allow runtime API key provision
