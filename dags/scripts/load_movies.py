import duckdb
import glob
import os
import sys
import subprocess

# Configurações de Ambiente
DB_PATH = os.getenv('DB_PATH', '/opt/airflow/data/entertainment.duckdb')
JSON_PATTERN = '/opt/airflow/data/raw/movies_*.json'
DBT_PROJECT_DIR = '/opt/airflow/entertainment_dbt'


def run_dbt():
    """
    Aciona o dbt para transformar os dados brutos de filmes.
    Isso garante que a tabela 'stg_movies' seja recriada para o Dashboard.
    """
    print("🚀 Iniciando transformações de filmes via dbt...")
    try:
        # Nota: O seletor deve bater com o nome do seu arquivo .sql (ex: stg_movies.sql)
        result = subprocess.run(
            [
                "dbt", "run",
                "--select", "stg_movies",
                "--project-dir", DBT_PROJECT_DIR,
                "--profiles-dir", DBT_PROJECT_DIR
            ],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ dbt output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar dbt:\n{e.stdout}\n{e.stderr}")
        raise


def load_movies():
    files = glob.glob(JSON_PATTERN)
    if not files:
        print(f"⚠️ Erro: Nenhum arquivo JSON encontrado em {JSON_PATTERN}")
        sys.exit(1)

    latest_file = max(files)
    print(f"📦 Carregando arquivo bruto de filmes: {latest_file}")

    con = None
    try:
        con = duckdb.connect(DB_PATH)
        con.execute("BEGIN TRANSACTION")

        # 1. Carga Bronze (Raw)
        # O dbt usará esta tabela como 'source' para gerar a stg_movies
        con.execute(
            f"CREATE OR REPLACE TABLE raw_movies_json AS SELECT * FROM read_json_auto('{latest_file}')")

        con.execute("COMMIT")
        print("✔️ Dados brutos de filmes enviados para raw_movies_json.")

        # Fechamos a conexão para o dbt poder assumir o controle do arquivo .duckdb
        con.close()

        # 2. Transformação Silver (dbt)
        run_dbt()

    except Exception as e:
        if con:
            try:
                con.execute("ROLLBACK")
                con.close()
            except:
                pass
        print(f"💥 Falha catastrófica na carga de filmes: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    load_movies()
