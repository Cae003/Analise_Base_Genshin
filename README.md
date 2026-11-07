
# ✦ Genshin Impact — Análise Histórica de Banners

Projeto desenvolvido para a disciplina **Python para Machine Learning e Inteligência Artificial**.

O objetivo é analisar o histórico de banners de personagens de **Genshin Impact**, identificando padrões de ausência, frequência de retorno e interesse dos jogadores, com foco na investigação de possíveis candidatos à versão **6.4 (Luna V)**.

## 📊 Funcionalidades

O dashboard possui três análises principais:

- **Análise 1 — Ausência e cronologia:** tempo desde a última aparição, intervalos históricos e linha do tempo dos banners.
- **Análise 2 — Frequência e retorno:** quantidade de aparições, intervalo médio entre banners e índice de ausência relativa.
- **Análise 3 — Interesse e características:** pulls acumulados e comparações entre características dos personagens.

Também é possível consultar a base de dados e aplicar filtros interativos.

## 🛠️ Tecnologias utilizadas

- **Python**
- **Pandas** — manipulação e tratamento dos dados
- **NumPy** — cálculos numéricos
- **Plotly** — gráficos interativos
- **Streamlit** — interface do dashboard

## 🚀 Como executar

### 1. Clone o repositório

```bash
git clone URL_DO_REPOSITORIO
cd NOME_DO_REPOSITORIO
```

### 2. Instale as dependências

```bash
pip install streamlit pandas numpy plotly
```

### 3. Execute o dashboard

Na pasta principal do projeto, execute:

```bash
streamlit run main.py
```

A aplicação será aberta no navegador, normalmente em:

http://localhost:8501

> **Importante:** o arquivo `arquivo.csv` deve estar na mesma pasta que o `main.py`.

## 📁 Estrutura do projeto

```text
projeto/
├── main.py
├── arquivo.csv
├── paginas/
│   ├── __init__.py
│   ├── dados.py
│   ├── componentes.py
│   ├── inicio.py
│   ├── analise1.py
│   ├── analise2.py
│   └── analise3.py
└── README.md
```

## 📝 Observações

- A base histórica possui data de referência de **24/02/2026**.
- A análise considera a versão **6.4 (Luna V)** como objetivo de investigação.
- Os resultados são exploratórios e **não representam previsões garantidas** sobre futuros banners.
