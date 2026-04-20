# 🎬 Entertainment Data Pipeline: TMDB & LastFM
![Dashboard do Projeto](assets/dashboard.png)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

Este projeto é um pipeline de dados **end-to-end** que extrai informações de cinema (TMDB) e música (LastFM) para gerar insights sobre tendências culturais, focado especialmente em dados do Brasil e do gênero K-Pop.

---

## 🛠️ Tecnologias e Arquitetura

O projeto utiliza o conceito de **Medallion Architecture** (Bronze, Silver) para processar os dados:

- **Orquestração:** [Airflow](https://airflow.apache.org/) (Dockerizado) para agendamento das extrações.
- **Ingestão:** Python (Requests) consumindo APIs REST.
- **Armazenamento:** [DuckDB](https://duckdb.org/) como Data Warehouse local de alta performance.
- **Transformação:** [dbt (data build tool)](https://www.getdbt.com/) para modelagem SQL e garantia de tipagem.
- **Visualização:** [Streamlit](https://streamlit.io/) para o dashboard interativo.

---

## 🏗️ Estrutura do Projeto

```text
├── assets/                 # Prints dos Dashboards (Streamlit)
├── dags/                   # DAGs do Airflow e scripts de ingestão (Python)
├── entertainment_dbt/      # Projeto dbt (Modelos SQL, Sources e Profiles)
│   ├── models/             # Camada de transformação (Silver)
│   └── profiles.yml        # Configuração de conexão com DuckDB
├── data/                   # Armazenamento local (Arquivos JSON e .duckdb)
└── app/                    # Código do Dashboard Streamlit

🚀 Como Executar
1. Pré-requisitos
Docker e Docker Compose instalados.

Chaves de API do TMDB e LastFM.

2. Configuração
Crie um arquivo .env na raiz do projeto:
TMDB_TOKEN=seu_token_aqui
LASTFM_API_KEY=sua_chave_aqui
AIRFLOW_UID=50000

3. Subindo o Ambiente
# Iniciar o Airflow
docker-compose up -d

# Instalar dependências do Dashboard (localmente se preferir)
pip install -r requirements.txt

# Rodar o Dashboard
streamlit run app/main.py

📊 Dashboard de Insights
O dashboard permite visualizar:

Filmes: Top 5 filmes com maior nota média nos últimos 30 dias.

Música: Comparativo de popularidade de artistas de K-Pop entre o público brasileiro e global.

👩‍💻 Autora
Rubia Massaud dos Santos
