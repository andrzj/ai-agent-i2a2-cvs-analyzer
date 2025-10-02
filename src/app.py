"""
CSV Analyzer AI Agent - Streamlit Application

Main application file for the CSV Analyzer AI Agent with Streamlit interface.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import logging
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
import io
import numpy as np

from config.settings import Settings
from utils.csv_loader import CSVLoader
from utils.data_processor import DataProcessor
from agent.csv_agent import CSVAgent

# ============================================================
# Logging Configuration
# ============================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('csv_analyzer.log')
    ]
)
logger = logging.getLogger(__name__)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title=Settings.APP_TITLE,
    page_icon=Settings.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# Session State Initialization
# ============================================================

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    logger.info("Initializing session state")
    
    if 'agent' not in st.session_state:
        st.session_state.agent = None
        logger.debug("Initialized agent state to None")
    
    if 'df' not in st.session_state:
        st.session_state.df = None
        logger.debug("Initialized df state to None")
    
    if 'dataset_info' not in st.session_state:
        st.session_state.dataset_info = None
        logger.debug("Initialized dataset_info state to None")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        logger.debug("Initialized messages state to empty list")
    
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
        logger.debug("Initialized file_uploaded state to False")
    
    if 'visualizations' not in st.session_state:
        st.session_state.visualizations = []


# ============================================================
# Helper Functions
# ============================================================

def load_csv_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Load CSV file and initialize agent.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Loaded DataFrame or None if error
    """
    try:
        logger.info(f"Starting to load CSV file: {uploaded_file.name}")
        
        # Save uploaded file temporarily
        temp_path = f"/tmp/{uploaded_file.name}"
        logger.debug(f"Saving file to temporary path: {temp_path}")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load CSV
        logger.info("Initializing CSVLoader")
        loader = CSVLoader()
        df, file_stats = loader.smart_load(temp_path)
        logger.info(f"Successfully loaded CSV: {df.shape[0]} rows, {df.shape[1]} columns")
        logger.debug(f"File stats: {file_stats}")
        
        # Store in session state
        st.session_state.df = df
        st.session_state.dataset_info = file_stats
        st.session_state.file_uploaded = True
        logger.info("Stored dataframe and file stats in session state")
        
        # Initialize agent
        logger.info("Initializing CSVAgent")
        agent = CSVAgent()
        agent.load_dataframe(df, file_stats)
        st.session_state.agent = agent
        logger.info("Agent initialized and stored in session state")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading CSV file: {str(e)}", exc_info=True)
        st.error(f"Error loading CSV file: {str(e)}")
        return None


def display_dataset_summary():
    """Display dataset summary in sidebar."""
    if st.session_state.agent is None:
        return
    
    summary = st.session_state.agent.get_dataset_summary()
    
    if summary:
        st.sidebar.markdown("### 📊 Resumo do Dataset")
        
        # Basic stats
        st.sidebar.metric("Linhas", f"{summary['shape']['rows']:,}")
        st.sidebar.metric("Colunas", f"{summary['shape']['columns']:,}")
        st.sidebar.metric("Memória", f"{summary['memory_usage_mb']:.2f} MB")
        
        # Column types
        st.sidebar.markdown("**Tipos de Colunas:**")
        col_types = summary['column_types']
        for col_type, count in col_types.items():
            if count > 0:
                st.sidebar.write(f"  • {col_type.title()}: {count}")
        
        # Missing values
        missing_pct = summary['missing_values']['missing_percentage']
        if missing_pct > 0:
            st.sidebar.warning(f"⚠️ {missing_pct:.1f}% valores ausentes")
        
        # Expandable column list
        with st.sidebar.expander("📋 Ver Todas as Colunas"):
            for col_type, cols in summary['columns_by_type'].items():
                if cols:
                    st.write(f"**{col_type.upper()}:**")
                    for col in cols:
                        st.write(f"  • {col}")


def display_suggested_questions():
    """Display suggested questions."""
    st.sidebar.markdown("### 💡 Perguntas Sugeridas")
    
    for i, question in enumerate(Settings.SUGGESTED_QUESTIONS):
        if st.sidebar.button(question, key=f"suggest_{i}"):
            logger.info(f"Suggested question clicked: {question}")
            
            # Add user message
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Get agent response
            try:
                logger.info("Processing suggested question with agent")
                response = st.session_state.agent.query(question)
                logger.info(f"Agent response received. Answer length: {len(response.get('answer', ''))} chars")
                
                # Clean up visualizations
                raw_visualizations = response.get('visualizations', [])
                visualizations = []
                for v in raw_visualizations:
                    if v and isinstance(v, str) and v.strip():
                        try:
                            json.loads(v)
                            visualizations.append(v)
                            logger.info(f"Valid visualization added (length: {len(v)} chars)")
                        except json.JSONDecodeError as e:
                            logger.warning(f"Skipping invalid visualization JSON: {str(e)}")
                
                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get('answer', '') or '',
                    "visualizations": visualizations
                })
                logger.info(f"Response added to messages. Total messages: {len(st.session_state.messages)}")
                
            except Exception as e:
                logger.error(f"Error processing suggested question: {str(e)}", exc_info=True)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Desculpe, encontrei um erro ao processar sua pergunta: {str(e)}",
                    "visualizations": []
                })
            
            # Rerun to display the response
            st.rerun()


def render_visualization(viz_json: str):
    """
    Render a Plotly visualization from JSON.
    
    Args:
        viz_json: JSON string of Plotly figure
    """
    try:
        # Skip if empty or whitespace
        if not viz_json or not viz_json.strip():
            return
        
        fig_dict = json.loads(viz_json)
        
        # Validate that we have a proper figure dict
        if not isinstance(fig_dict, dict):
            return
        
        fig = go.Figure(fig_dict)
        st.plotly_chart(fig, use_container_width=True)
        
        # Store visualization for gallery
        if viz_json not in st.session_state.visualizations:
            st.session_state.visualizations.append(viz_json)
    except json.JSONDecodeError:
        # Silently skip invalid JSON visualizations
        pass
    except Exception as e:
        logger.error(f"Error rendering visualization: {str(e)}")
        st.error(f"Error rendering visualization: {str(e)}")


def process_user_message(user_message: str):
    """
    Process user message and get agent response.
    
    Args:
        user_message: User's question
    """
    if st.session_state.agent is None:
        st.error("Por favor, faça upload de um arquivo CSV primeiro!")
        return
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Get agent response
    with st.spinner("🤔 Analyzing..."):
        response = st.session_state.agent.query(user_message)
    
    # Add AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response['answer'],
        "visualizations": response.get('visualizations', [])
    })


def export_analysis_to_markdown() -> str:
    """
    Export the entire conversation and analysis to Markdown format.
    
    Returns:
        Markdown formatted string of the analysis
    """
    md_content = f"""# Relatório de Análise CSV

**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---

## Informações do Dataset

"""
    
    # Add dataset summary
    if st.session_state.dataset_info:
        info = st.session_state.dataset_info
        md_content += f"""
- **Nome do Arquivo:** {info.get('file_name', 'N/A')}
- **Linhas:** {info.get('num_rows', 0):,}
- **Colunas:** {info.get('num_columns', 0)}
- **Tamanho:** {info.get('file_size_mb', 0):.2f} MB
- **Codificação:** {info.get('encoding', 'N/A')}

"""
    
    # Add conversation history
    md_content += """---

## Conversa da Análise

"""
    
    for i, msg in enumerate(st.session_state.messages, 1):
        role = "**Usuário**" if msg['role'] == 'user' else "**Assistente IA**"
        md_content += f"""
### {role}

{msg['content']}

"""
    
    # Add memory summary
    if st.session_state.agent:
        memory_export = st.session_state.agent.memory.export_history()
        if memory_export.get('conclusions'):
            md_content += """---

## Conclusões Principais

"""
            for conclusion in memory_export['conclusions']:
                md_content += f"- {conclusion}\n"
    
    md_content += """
---

*Gerado pelo CSV Analyzer AI Agent*
"""
    
    return md_content


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert NumPy/Pandas types to JSON-serializable Python types.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    else:
        return obj


def export_analysis_to_json() -> str:
    """
    Export the entire analysis to JSON format.
    
    Returns:
        JSON formatted string of the analysis
    """
    logger.info("Starting JSON export")
    try:
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'dataset_info': st.session_state.dataset_info,
            'conversation': st.session_state.messages,
            'total_messages': len(st.session_state.messages),
            'total_visualizations': len(st.session_state.visualizations)
        }
        logger.debug(f"Export data structure created with {len(st.session_state.messages)} messages")
        
        # Add memory data if available
        if st.session_state.agent:
            export_data['memory'] = st.session_state.agent.memory.export_history()
            logger.debug("Memory data added to export")
        
        # Convert NumPy/Pandas types to JSON-serializable types
        logger.debug("Converting data types for JSON serialization")
        export_data = convert_to_json_serializable(export_data)
        
        json_str = json.dumps(export_data, indent=2)
        logger.info(f"JSON export completed. Size: {len(json_str)} chars")
        return json_str
    except Exception as e:
        logger.error(f"Error during JSON export: {str(e)}", exc_info=True)
        raise


def display_export_options():
    """Display export options in sidebar."""
    st.sidebar.markdown("### 💾 Exportar Análise")
    
    col1, col2 = st.sidebar.columns(2)
    
    # Export as Markdown
    with col1:
        md_content = export_analysis_to_markdown()
        st.download_button(
            label="📄 Markdown",
            data=md_content,
            file_name=f"analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            help="Baixar conversa como arquivo Markdown"
        )
    
    # Export as JSON
    with col2:
        json_content = export_analysis_to_json()
        st.download_button(
            label="📊 JSON",
            data=json_content,
            file_name=f"analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Baixar dados completos da análise como JSON"
        )


def display_visualization_gallery():
    """Display a gallery of all generated visualizations."""
    if not st.session_state.visualizations:
        st.info("Nenhuma visualização gerada ainda. Peça ao agente para criar alguns gráficos!")
        return
    
    st.markdown(f"### 📊 Galeria de Visualizações ({len(st.session_state.visualizations)} gráficos)")
    
    # Display visualizations in a grid
    num_cols = 2
    cols = st.columns(num_cols)
    
    for idx, viz_json in enumerate(st.session_state.visualizations):
        col_idx = idx % num_cols
        with cols[col_idx]:
            try:
                fig_dict = json.loads(viz_json)
                fig = go.Figure(fig_dict)
                
                # Get chart title or create default
                title = fig_dict.get('layout', {}).get('title', {})
                if isinstance(title, dict):
                    chart_title = title.get('text', f'Gráfico {idx + 1}')
                else:
                    chart_title = str(title) if title else f'Gráfico {idx + 1}'
                
                with st.expander(f"📈 {chart_title}", expanded=True):
                    st.plotly_chart(fig, use_container_width=True, key=f"gallery_chart_{idx}")
                    
                    # Add download button for individual chart
                    st.download_button(
                        label="💾 Baixar Gráfico JSON",
                        data=viz_json,
                        file_name=f"grafico_{idx + 1}.json",
                        mime="application/json",
                        key=f"download_viz_{idx}"
                    )
            except Exception as e:
                st.error(f"Erro ao renderizar gráfico {idx + 1}: {str(e)}")


# ============================================================
# Main Application
# ============================================================

def main():
    """Main application function."""
    logger.info("=" * 60)
    logger.info("Starting CSV Analyzer AI Agent application")
    logger.info("=" * 60)
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title(Settings.APP_TITLE)
    st.markdown("Faça perguntas sobre seus dados CSV em linguagem natural!")
    
    # ========================================
    # Sidebar
    # ========================================
    
    with st.sidebar:
        st.markdown("## 📁 Upload de Arquivo CSV")
        
        uploaded_file = st.file_uploader(
            "Escolha um arquivo CSV",
            type=['csv'],
            help=f"Tamanho máximo do arquivo: {Settings.MAX_FILE_SIZE_MB}MB"
        )
        
        if uploaded_file is not None:
            logger.info(f"File uploaded: {uploaded_file.name}, size: {uploaded_file.size} bytes")
            if not st.session_state.file_uploaded or \
               st.session_state.dataset_info.get('file_name') != uploaded_file.name:
                logger.info("New file detected, initiating load process")
                
                with st.spinner("Carregando arquivo CSV..."):
                    df = load_csv_file(uploaded_file)
                
                if df is not None:
                    logger.info(f"File loaded successfully: {len(df):,} rows")
                    st.success(f"✅ Carregado {len(df):,} linhas com sucesso!")
                    st.session_state.messages = []  # Clear chat on new file
                    logger.info("Chat history cleared for new file")
                else:
                    logger.warning("File load returned None")
        
        # Display dataset summary if file is loaded
        if st.session_state.file_uploaded:
            st.markdown("---")
            display_dataset_summary()
            
            st.markdown("---")
            display_suggested_questions()
            
            # Show export options if there are messages
            if st.session_state.messages:
                st.markdown("---")
                display_export_options()
            
            st.markdown("---")
            
            # Clear chat button
            if st.button("🗑️ Limpar Histórico do Chat"):
                st.session_state.messages = []
                st.session_state.visualizations = []
                if st.session_state.agent:
                    st.session_state.agent.reset_memory()
                st.rerun()
            
            # Reset/New file button
            if st.button("📤 Carregar Novo Arquivo"):
                st.session_state.file_uploaded = False
                st.session_state.df = None
                st.session_state.agent = None
                st.session_state.messages = []
                st.session_state.visualizations = []
                st.rerun()
    
    # ========================================
    # Main Chat Area
    # ========================================
    
    if not st.session_state.file_uploaded:
        # Show welcome message
        st.info("👈 Por favor, faça upload de um arquivo CSV para começar!")
        
        st.markdown("""
        ### O que este agente pode fazer?
        
        Depois de carregar um arquivo CSV, você pode fazer perguntas sobre:
        
        - **Descrição de Dados**: Tipos, distribuições, intervalos, estatísticas
        - **Análise de Padrões**: Tendências, frequências, clusters
        - **Detecção de Outliers**: Identificar e analisar valores atípicos
        - **Relacionamentos**: Correlações, dependências, influências
        - **Visualizações**: Gráficos, plots e mapas de calor
        
        O agente lembra suas perguntas anteriores e constrói sobre análises anteriores!
        """)
        
        # Show example
        with st.expander("📖 Exemplos de Perguntas"):
            st.markdown("""
            - "Quais são os tipos de dados de cada coluna?"
            - "Mostre-me a distribuição da coluna idade"
            - "Existem valores atípicos nos dados de salário?"
            - "Qual é a correlação entre idade e renda?"
            - "Você pode identificar padrões temporais nos dados de vendas?"
            - "Quais variáveis influenciam mais a rotatividade de clientes?"
            - "Crie um gráfico de dispersão de preço vs quantidade"
            """)
    
    else:
        # Create tabs for Chat and Visualization Gallery
        tab1, tab2 = st.tabs(["💬 Chat", "🖼️ Galeria de Visualizações"])
        
        with tab1:
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    # Ensure content exists and is not empty
                    content = message.get("content", "")
                    if content and content.strip():
                        st.markdown(content)
                    
                    # Render visualizations if present
                    visualizations = message.get("visualizations", [])
                    if message["role"] == "assistant" and visualizations:
                        for viz_json in visualizations:
                            if viz_json and isinstance(viz_json, str) and viz_json.strip():
                                render_visualization(viz_json)
            
            # Chat input
            if prompt := st.chat_input("Faça uma pergunta sobre seus dados..."):
                logger.info(f"Received user query: {prompt}")
                
                # Process query with agent
                with st.spinner("🤔 Analisando..."):
                    logger.info("Processing query with agent")
                    try:
                        response = st.session_state.agent.query(prompt)
                        logger.info(f"Agent response received. Answer length: {len(response.get('answer', ''))} chars")
                        logger.debug(f"Visualizations count: {len(response.get('visualizations', []))}")
                    except Exception as e:
                        logger.error(f"Error processing query: {str(e)}", exc_info=True)
                        st.error(f"Erro ao processar consulta: {str(e)}")
                        response = {'answer': 'Desculpe, encontrei um erro ao processar sua consulta.', 'visualizations': []}
                
                # Store in messages
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Log the raw response for debugging
                logger.info(f"Raw visualizations received: {len(response.get('visualizations', []))}")
                if response.get('visualizations'):
                    for idx, v in enumerate(response['visualizations']):
                        logger.info(f"Viz {idx}: type={type(v)}, len={len(str(v)) if v else 0}, preview={str(v)[:100]}")
                
                # Clean up visualizations - remove empty strings and ensure valid JSON strings
                raw_visualizations = response.get('visualizations', [])
                visualizations = []
                for v in raw_visualizations:
                    if v and isinstance(v, str) and v.strip():
                        try:
                            # Validate it's proper JSON
                            json.loads(v)
                            visualizations.append(v)
                            logger.info(f"Valid visualization added (length: {len(v)} chars)")
                        except json.JSONDecodeError as e:
                            logger.warning(f"Skipping invalid visualization JSON: {str(e)} - {v[:100]}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.get('answer', '') or '',  # Ensure never None
                    "visualizations": visualizations
                })
                logger.info(f"Message history updated. Total messages: {len(st.session_state.messages)}, visualizations: {len(visualizations)}")
                
                # Rerun to display the new messages
                st.rerun()
        
        with tab2:
            # Display visualization gallery
            display_visualization_gallery()
    
    # ========================================
    # Footer
    # ========================================
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Desenvolvido com ❤️ usando Streamlit e LangChain"
        "</div>",
        unsafe_allow_html=True
    )
    
    logger.info("Main function completed successfully")


# ============================================================
# Run Application
# ============================================================

if __name__ == "__main__":
    logger.info("Application entry point reached")
    try:
        main()
    except Exception as e:
        logger.critical(f"Critical error in main application: {str(e)}", exc_info=True)
        st.error(f"A critical error occurred: {str(e)}")
        raise
