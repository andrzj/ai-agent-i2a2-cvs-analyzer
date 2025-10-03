# CSV Analyzer AI Agent 📊🤖

> **✅ STATUS: PRONTO PARA USO** | Todas as 19 ferramentas implementadas | Interface Streamlit completa

Um agente inteligente alimentado por IA que analisa arquivos CSV grandes (até 150MB+) e responde perguntas sobre padrões de dados, distribuições, correlações e valores atípicos através de uma interface conversacional.

## 🚀🚀🚀 Início Rápido - Automático (2 minutos)

```bash
./check_environment.sh   # Verifica ambiente
./setup.sh               # Setup inicial (rode só 1 vez)
./run.sh                 # Roda a aplicação
```

## 🚀 Início Rápido - Manual (5 minutos)

```bash
# 1. Verifique o status do seu ambiente
./check_environment.sh

# 2. Configure (se necessário)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env e adicione sua chave da API OpenAI

# 3. Gere dados de exemplo (opcional)
cd src && python3 generate_sample_data.py && cd ..

# 4. Inicie o aplicativo!
cd src && streamlit run app.py
```

## Recursos ✨

- **Interface Conversacional**: Faça perguntas em linguagem natural sobre seus dados
- **Suporte a Arquivos Grandes**: Manipule arquivos CSV de até 200MB com eficiência
- **Análise Abrangente**:
  - Detecção de tipos de dados e análise de distribuição
  - Identificação de padrões e tendências
  - Detecção de outliers e análise de impacto
  - Descoberta de correlações e relacionamentos
  - Visualizações interativas
- **Com Memória**: O agente lembra análises e conclusões anteriores
- **Arquitetura Baseada em Ferramentas**: LLM apenas para compreensão de intenção, processamento de dados feito em Python

## Arquitetura 🏗️

```
Pergunta do Usuário → LLM (Intenção) → Seleção de Ferramenta → Análise Python → Visualização → Resposta
```

📖 **Veja a Arquitetura do Sistema em [ARCHITECTURE.md](ARCHITECTURE.md)** | Entenda como o sistema funciona | System Design

## Instalação 🚀

### Pré-requisitos
- Python 3.9+
- Chave da API OpenAI (ou outro provedor de LLM)

### Configuração

1. Clone o repositório:
```bash
git clone <repository-url>
cd ai-agent-i2a2-cvs-analyzer
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env e adicione suas chaves de API
```

## Uso 💡

1. Inicie o aplicativo Streamlit:
```bash
streamlit run src/app.py
```

2. Abra seu navegador em `http://localhost:8501`

3. Faça upload de um arquivo CSV

4. Comece a fazer perguntas como:
   - "Quais são os tipos de dados de cada coluna?"
   - "Mostre-me a distribuição da coluna idade"
   - "Existem valores atípicos nos dados de salário?"
   - "Qual é a correlação entre idade e renda?"
   - "Mostre-me tendências temporais nos dados de vendas"

## Estrutura do Projeto 📁

```
csv-analyzer-agent/
├── 🔧 setup.sh                       ← ⭐ Setup automatico script
├── 🚀 run.sh                         ← ⭐ Roda aplicação
├── 🔍 check_environment.sh           ← Verifica ambiente
│
├── 📋 requirements.txt               ← Dependencias Python
├── 🔐 .env.example                   ← Template de configuração
├── 🙈 .gitignore                     ← Git exclusions
│
├── 📊 sample_data_*.csv              ← Datasets de teste(generated)
│
├── 📁 src/
│   ├── app.py                        ← ⭐ Streamlit UI
│   ├── generate_sample_data.py       ← Gerador de dados de exemplo
│   │
│   ├── config/
│   │   └── settings.py               ← ⚙️ Constantes de configuração
│   │
│   ├── utils/
│   │   ├── csv_loader.py             ← 📥 Utilitários de carregamento CSV
│   │   └── data_processor.py         ← 🔍 Detecção de tipos
│   │
│   ├── tools/                        ← 🛠️ Ferramentas de análise
│   │   ├── data_description.py       ← Ferramentas de tipo de dados e estatísticas
│   │   ├── pattern_analysis.py       ← Ferramentas de padrões e tendências
│   │   ├── outlier_detection.py      ← Ferramentas de detecção de outliers
│   │   ├── relationship_analysis.py  ← Ferramentas de correlação
│   │   └── visualization.py          ← Ferramentas de geração de gráficos
│   │
│   └── agent/
│       ├── memory.py                 ← 🧠 Sisterma de memória do agente
│       └── csv_agent.py              ← 🤖 AI Agente
```

## Stack de Tecnologia

### 🎨 Frontend

- Streamlit 1.28.0+ Interface de interface web e chat

### 🤖 IA/Agente
- LangChain 0.1.0+ Framework de agente
- LangChain-OpenAI 0.0.5+ Integração LLM
- OpenAI gpt-4o-mini Compreensão de intenção

### 📊 Processamento De Dados
- Pandas 2.0.0+ Manipulação de DataFrames e CSV
- NumPy 1.24.0+ Operações numéricas

### 🔬 Análise
- Scikit-learn 1.3.0+ Clusterização, importância de recursos
- SciPy 1.11.0+ Testes estatísticos

### 📈 Visualização
- Plotly 5.17.0+ Gráficos interativos (primário)
- Matplotlib 3.7.0+ Gráficos estáticos
- Seaborn Visualizações estatísticas 0.12.0+

### 🛠️ Utilitários
- Chardet 5.2.0+ Detecção de codificação
- Python-dotenv 1.0.0+ Configuração de ambiente

## Ferramentas Disponíveis 🔧

O agente tem acesso a 19 ferramentas especializadas:

**📊 Descrição de Dados (5 ferramentas)**
1. `get_data_types` - Detecção de tipo de dados
2. `get_distribution_stats` - Estatísticas de distribuição
3. `get_range_info` - Informações de intervalo
4. `calculate_central_tendency` - Medidas de tendência central
5. `calculate_variability` - Cálculos de variabilidade

**📈 Análise de Padrões (3 ferramentas)**
6. `detect_temporal_patterns` - Detecção de padrões temporais
7. `get_frequency_analysis` - Análise de frequência
8. `detect_clusters` - Detecção de clusters

**⚠️ Detecção de Outliers (3 ferramentas)**
9. `detect_outliers_iqr` - Detecção de outliers baseada em IQR
10. `detect_outliers_zscore` - Detecção de outliers por Z-score
11. `analyze_outlier_impact` - Análise de impacto de outliers

**🔗 Análise de Relacionamentos (3 ferramentas)**
12. `calculate_correlation` - Cálculo de correlação
13. `analyze_variable_relationships` - Análise de relacionamento entre variáveis
14. `identify_influential_variables` - Identificação de variáveis influentes

**📉 Visualização (5 ferramentas)**
15. `create_histogram` - Histogramas
16. `create_scatter_plot` - Gráficos de dispersão
17. `create_correlation_heatmap` - Mapas de calor de correlação
18. `create_box_plot`- Box plots
19. `create_time_series_plot` - Gráficos de séries temporais

## Exemplos de Perguntas 💬

### Descrição de Dados
- "Quais colunas estão neste dataset?"
- "Qual é a distribuição das colunas numéricas?"
- "Mostre-me o intervalo e a média da coluna preço"

### Análise de Padrões
- "Existem tendências temporais nos dados de vendas?"
- "Quais são as categorias mais frequentes?"
- "Você pode identificar clusters nestes dados?"

### Detecção de Outliers
- "Encontre outliers na coluna receita"
- "Como os outliers afetam a média?"
- "Devo remover estes outliers?"

### Relacionamentos
- "Qual é a correlação entre idade e salário?"
- "Quais variáveis influenciam mais a rotatividade de clientes?"
- "Mostre-me um gráfico de dispersão de preço vs quantidade"

## 💡 Dicas Pro

1. **Seja Específico:** Em vez de "analisar estes dados", pergunte "qual é a correlação entre vendas e quantidade?"

2. **Use Acompanhamentos:** O agente tem memória! Faça perguntas complementares como "conte-me mais sobre esses valores discrepantes"

3. **Combine Ferramentas:** Faça perguntas complexas como "encontre valores discrepantes na receita e mostre seu impacto nas vendas médias"

4. **Solicite Visualizações:** Diga "mostre-me um gráfico" ou "crie um gráfico" para obter representações visuais

5. **Verifique a Barra Lateral:** Use perguntas sugeridas para explorar seus dados mais rapidamente

6. **Exportar Análise:** O agente se lembra de todas as análises - você pode perguntar "resuma o que descobrimos até agora"

## 🔑 Configuração da Chave de API

A aplicação suporta **duas maneiras** de fornecer sua chave de API OpenAI:

#### Opção 1: Variável de Ambiente (Recomendado para Desenvolvimento)
Edite o arquivo `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
```

#### Opção 2: Entrada em Tempo de Execução (Fácil de Usar)

- **Não é necessário arquivo .env!**
- Forneça sua chave de API diretamente na interface do aplicativo
- A chave é armazenada apenas para a sessão atual (segura e temporária)
- Perfeito para:
  - Demonstrações rápidas
  - Ambientes compartilhados
  - Usuários sem acesso à configuração do ambiente

## Configuração ⚙️

Edite o arquivo `.env` para personalizar:

- `OPENAI_API_KEY`: API key do modelo LLM (opcional - pode fornecer via UI)
- `LLM_MODEL`: Escolha seu modelo LLM (padrão: gpt-4o-mini)
- `MAX_FILE_SIZE_MB`: Tamanho máximo do arquivo CSV (padrão: 200)
- `MAX_CONVERSATION_HISTORY`: Comprimento do histórico de chat (padrão: 50)

## Desenvolvimento 🛠️

### Adicionando Novas Ferramentas
1. Crie a função da ferramenta no arquivo apropriado em `src/tools/`
2. Adicione a ferramenta à inicialização do agente em `src/agent/csv_agent.py`
3. Documente o uso da ferramenta no README

## Limitações ⚠️

- Apenas arquivos CSV
- Uso de memória proporcional ao tamanho do arquivo
- Junções/mesclagens complexas não suportadas
- Atualizações de dados em tempo real não suportadas

## Roadmap 🗺️

- [ ] Suporte para arquivos Excel
- [ ] Análise de múltiplos arquivos
- [ ] Endpoint de API para integração

## Contribuindo 🤝

Contribuições são bem-vindas! Por favor:
1. Faça um fork do repositório
2. Crie uma branch de funcionalidade
3. Adicione testes para novas funcionalidades
4. Envie um pull request

## Licença 📄

Licença MIT - veja o arquivo LICENSE para detalhes

## Suporte 💬

Para perguntas ou problemas, por favor abra uma issue no GitHub.

---

Desenvolvido com ❤️ usando Streamlit e LangChain
