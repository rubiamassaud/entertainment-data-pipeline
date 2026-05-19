from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta
import requests
import json
import os

TMDB_TOKEN = os.getenv("TMDB_TOKEN")
RAW_PATH = "/opt/airflow/data/raw"

def fetch_popular_movies():
    # ... (seu código de fetch permanece igual, ele está ótimo)
    url = "https://api.themoviedb.org/3/movie/popular?language=pt-BR&page=1"
    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    os.makedirs(RAW_PATH, exist_ok=True)
    filename = f"{RAW_PATH}/movies_{datetime.now().strftime('%Y%m%d')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Salvou {len(data['results'])} filmes em {filename}")

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="tmdb_popular_movies",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["tmdb", "entretenimento"],
) as dag:

    fetch_movies = PythonOperator(
        task_id="fetch_popular_movies",
        python_callable=fetch_popular_movies,
    )

    # 1. Carrega o JSON bruto para o DuckDB
    load_to_duckdb = BashOperator(
        task_id="load_to_duckdb",
        bash_command="python /opt/airflow/dags/scripts/load_movies.py 2>&1",
    )

    # 2. NOVA TASK: O dbt entra em cena para criar a stg_movies
    dbt_transform = BashOperator(
        task_id="dbt_transform_movies",
        bash_command=(
            "cd /opt/airflow/entertainment_dbt && "
            "dbt run --select stg_movies --profiles-dir . --project-dir ."
        ),
        append_env=True,
    )

    # O fluxo completo: Extrair -> Carregar -> Transformar (dbt)
    fetch_movies >> load_to_duckdb >> dbt_transform
