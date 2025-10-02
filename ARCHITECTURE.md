# CSV Analyzer AI Agent - Arquitetura do Sistema

```
┌───────────────────────────────────────────────────────────────────┐
│                       INTERFACE WEB STREAMLIT                     │
│                         (src/app.py)                              │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ Upload Arquivo │  │  Interface Chat  │  │  Visualizações   │   │
│  │   Barra Lateral│  │   (Mensagens)    │  │   (Plotly)       │   │
│  └────────────────┘  └──────────────────┘  └──────────────────┘   │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                    AGENTE CSV (LangChain)                         │
│                    (src/agent/csv_agent.py)                       │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │  LLM (gpt-4o-mini)                                        │    │
│  │  • Compreende a intenção do usuário                       │    │
│  │  • Seleciona ferramentas apropriadas                      │    │
│  │  • Gera respostas em linguagem natural                    │    │
│  │  • NUNCA recebe dados CSV brutos                          │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Sistema de Memória (src/agent/memory.py)                  │   │
│  │  • Histórico de conversação                                │   │
│  │  • Rastreamento de resultados de análise                   │   │
│  │  • Armazenamento de conclusões                             │   │
│  │  • Auto-sumarização (>20 turnos)                           │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                   ORQUESTRAÇÃO DE FERRAMENTAS                     │
│                                                                   │
│  ┌──────────────────────┐  ┌──────────────────────┐               │
│  │  Descrição de Dados  │  │  Análise de Padrões  │               │
│  │  (5 ferramentas)     │  │  (3 ferramentas)     │               │
│  │  • Tipos de dados    │  │  • Padrões temporais │               │
│  │  • Distribuição      │  │  • Frequência        │               │
│  │  • Info de intervalo │  │  • Clustering        │               │
│  │  • Tendência central │  │                      │               │
│  │  • Variabilidade     │  │                      │               │
│  └──────────────────────┘  └──────────────────────┘               │
│                                                                   │
│  ┌──────────────────────┐  ┌──────────────────────┐               │
│  │  Detecção Outliers   │  │  Análise de          │               │
│  │  (3 ferramentas)     │  │  Relacionamentos     │               │
│  │  • Método IQR        │  │  (3 ferramentas)     │               │
│  │  • Método Z-score    │  │  • Correlação        │               │
│  │  • Análise de impacto│  │  • Relacionamentos   │               │
│  └──────────────────────┘  │  • Import. recursos  │               │
│                            └──────────────────────┘               │
│  ┌──────────────────────┐                                         │
│  │  Visualização        │                                         │
│  │  (5 ferramentas)     │                                         │
│  │  • Histograma        │                                         │
│  │  • Gráfico dispersão │                                         │
│  │  • Mapa de calor     │                                         │
│  │  • Box plot          │                                         │
│  │  • Série temporal    │                                         │
│  └──────────────────────┘                                         │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                  CAMADA DE PROCESSAMENTO DE DADOS                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Carregador CSV (src/utils/csv_loader.py)                  │   │
│  │  • Detecção de codificação (chardet)                       │   │
│  │  • Validação de arquivo (tamanho, formato)                 │   │
│  │  • Leitura em blocos (arquivos >50MB)                      │   │
│  │  • Estratégia de carregamento inteligente                  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Processador de Dados (src/utils/data_processor.py)        │   │
│  │  • Detecção tipo coluna (numérico, categórico, datetime)   │   │
│  │  • Tratamento de valores ausentes                          │   │
│  │  • Geração de resumo de dados                              │   │
│  │  • Amostragem inteligente (datasets grandes)               │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                   BIBLIOTECAS DE ANÁLISE                          │
│                                                                   │
│  Pandas • NumPy • Scikit-learn • SciPy • Plotly • Matplotlib      │
│                                                                   │
│  • Computações estatísticas                                       │
│  • Aprendizado de máquina (clustering, importância de recursos)   │
│  • Análise de correlação (Pearson, Spearman)                      │
│  • Visualizações interativas (formato JSON)                       │
└───────────────────────────────────────────────────────────────────┘


FLUXO DE DADOS:
───────────────

  Pergunta do Usuário
       │
       ▼
  Interface Streamlit ────────────────┐
       │                              │
       ▼                              │
  Agente CSV (LangChain)              │
       │                              │
       ├─→ LLM (Apenas Intenção)      │
       │   • Sem dados CSV            │
       │   • Seleção de ferramenta    │
       │                              │
       ├─→ Sistema de Memória         │
       │   • Contexto anterior        │
       │   • Histórico de análise     │
       │                              │
       ▼                              │
  Execução de Ferramenta              │
       │                              │
       ├─→ Descrição de Dados         │
       ├─→ Análise de Padrões         │
       ├─→ Detecção de Outliers       │
       ├─→ Análise de Relacionamentos │
       ├─→ Visualização               │
       │                              │
       ▼                              │
  Processamento Python                │
       │                              │
       ├─→ Pandas/NumPy               │
       ├─→ Scikit-learn               │
       ├─→ SciPy                      │
       ├─→ Plotly                     │
       │                              │
       ▼                              │
  Resultado (Texto + JSON)            │
       │                              │
       ▼                              │
  Formatação do Agente ◄──────────────┘
       │
       ▼
  Exibição Streamlit
       │
       ├─→ Resposta em Texto
       └─→ Gráfico Plotly


PRINCÍPIOS FUNDAMENTAIS:
────────────────────────

1. LLM Apenas para Intenção
   • Dados CSV NUNCA enviados ao LLM
   • Apenas descrições de ferramentas e resultados
   • Mantém custos baixos e dados privados

2. Arquitetura Baseada em Ferramentas
   • Cada ferramenta é uma função Python especializada
   • Ferramentas recebem DataFrame diretamente
   • Ferramentas retornam strings formatadas ou JSON

3. Gerenciamento de Memória
   • Rastreia todas as conversas
   • Armazena metadados de análise
   • Auto-sumariza quando limite é atingido
   • Permite perguntas de acompanhamento

4. Manipulação Eficiente de Arquivos
   • Detecção de codificação para dados internacionais
   • Leitura em blocos para arquivos grandes (>50MB)
   • Amostragem inteligente para datasets muito grandes (>100K linhas)
   • Suporta arquivos até 150MB

5. Visualizações Interativas
   • Ferramentas retornam "PLOT_JSON:{json_string}"
   • App analisa e renderiza com Plotly
   • Gráficos interativos (zoom, pan, hover)
   • Tamanho padrão 800x600px


CONFIGURAÇÃO:
─────────────

Todas as configurações em src/config/settings.py:

• LLM: Modelo, temperatura, prompt do sistema
• Arquivos: Tamanho máx (200MB), tamanho do bloco (50K linhas)
• Estatísticas: Multiplicador IQR (1.5), limite Z-score (3.0)
• Memória: Limite de resumo (20 turnos), máx armazenado (50)
• Visualização: Dimensões padrão (800x600px)


PILHA DE TECNOLOGIA:
────────────────────

Frontend:
• Streamlit 1.28.0+ (Interface Web, interface de chat)

IA/Agente:
• LangChain 0.1.0+ (Framework de agente)
• LangChain-OpenAI 0.0.5+ (Integração LLM)
• OpenAI gpt-4o-mini (Compreensão de intenção)

Processamento de Dados:
• Pandas 2.0.0+ (DataFrames, manipulação CSV)
• NumPy 1.24.0+ (Operações numéricas)

Análise:
• Scikit-learn 1.3.0+ (Clustering, importância de recursos)
• SciPy 1.11.0+ (Testes estatísticos)

Visualização:
• Plotly 5.17.0+ (Gráficos interativos)
• Matplotlib 3.7.0+ (Gráficos estáticos)
• Seaborn 0.12.0+ (Visualizações estatísticas)

Utilitários:
• Chardet 5.2.0+ (Detecção de codificação)
• Python-dotenv 1.0.0+ (Configuração de ambiente)


ESTRUTURA DE ARQUIVOS:
──────────────────────

src/
├── app.py                    # Interface Streamlit (350+ linhas)
├── config/
│   └── settings.py           # Configuração (150+ configurações)
├── utils/
│   ├── csv_loader.py         # Carregamento de arquivo
│   └── data_processor.py     # Detecção de tipo
├── tools/
│   ├── data_description.py   # 5 ferramentas
│   ├── pattern_analysis.py   # 3 ferramentas
│   ├── outlier_detection.py  # 3 ferramentas
│   ├── relationship_analysis.py # 3 ferramentas
│   └── visualization.py      # 5 ferramentas
└── agent/
    ├── memory.py             # Sistema de memória
    └── csv_agent.py          # Agente principal


DESEMPENHO:
───────────

• Tempo de resposta: <5s (maioria das consultas)
• Tamanho do arquivo: Até 150MB
• Buffer de memória: 50 conversas
• Auto-amostragem: >100K linhas
• Leitura em blocos: arquivos >50MB
• Ferramentas: 19 funções especializadas


SEGURANÇA:
──────────

• Chaves de API em .env (não commitadas)
• Nenhum dado enviado ao contexto do LLM
• Processamento de arquivo apenas local
• Limites de tamanho de arquivo configuráveis
• Validação de entrada em uploads
```
