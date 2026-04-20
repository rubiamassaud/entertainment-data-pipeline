import duckdb
import glob
import os
import sys
import subprocess

# Configurações de Ambiente
DB_PATH = os.getenv('DB_PATH', '/opt/airflow/data/entertainment.duckdb')
JSON_PATTERN = '/opt/airflow/data/raw/top10_brazil_*.json'
DBT_PROJECT_DIR = '/opt/airflow/entertainment_dbt'

def run_dbt():
    print("🚀 Iniciando transformações via dbt...")
    try:
        # DICA: Verifique se o nome do modelo é exatamente 'stg_lastfm'
        result = subprocess.run(
            [
                "dbt", "run", 
                "--select", "stg_lastfm", # Ajustado para o nome comum do modelo
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
        raise # Garante que o load_data pegue o erro e dê exit(1)

def load_data():
    files = glob.glob(JSON_PATTERN)
    if not files:
        print(f"⚠️ Erro: Nenhum arquivo JSON encontrado em {JSON_PATTERN}")
        sys.exit(1)

    latest_file = max(files)
    print(f"📦 Carregando arquivo: {latest_file}")
    con = None
    
    try:
        con = duckdb.connect(DB_PATH)
        con.execute("BEGIN TRANSACTION")
        
        # 1. Carga Raw (Bronze Layer)
        con.execute("DROP TABLE IF EXISTS top10_brazil_artists")
        con.execute(f"CREATE TABLE top10_brazil_artists AS SELECT * FROM read_json_auto('{latest_file}')")
        
        con.execute("COMMIT")
        print("✔️ Carga bruta concluída com sucesso.")
        
        # Fechamento obrigatório para liberar o arquivo .duckdb para o dbt
        con.close()
        
        # 2. Transformação (Silver Layer via dbt)
        run_dbt()

    except Exception as e:
        if con:
            try:
                con.execute("ROLLBACK")
                con.close()
            except:
                pass
        print(f"💥 Falha catastrófica: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    load_data()