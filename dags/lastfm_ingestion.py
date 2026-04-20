from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta
import requests
import json
import os
import logging

logger = logging.getLogger("airflow.task")

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_URL = "https://ws.audioscrobbler.com/2.0/"
RAW_PATH = "/opt/airflow/data/raw"


def get_top_artists_brazil():
    response = requests.get(LASTFM_URL, params={
        "method": "geo.gettopartists",
        "country": "brazil",
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 200
    })
    response.raise_for_status()
    artists = response.json()["topartists"]["artist"]

    return [
        {
            "rank": int(a["@attr"]["rank"]),
            "name": a["name"],
            "listeners_brazil": int(a["listeners"]),
            "lastfm_url": a["url"],
            "mbid": a.get("mbid")
        }
        for a in artists
    ]


def get_artist_info(artist_name):
    response = requests.get(LASTFM_URL, params={
        "method": "artist.getinfo",
        "artist": artist_name,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    })
    response.raise_for_status()
    data = response.json().get("artist", {})

    stats = data.get("stats", {})
    tags = [t["name"] for t in data.get("tags", {}).get("tag", [])]
    similar = [a["name"] for a in data.get("similar", {}).get("artist", [])]

    return {
        "listeners_global": int(stats.get("listeners", 0)),
        "playcount_global": int(stats.get("playcount", 0)),
        "ontour": data.get("ontour") == "1",
        "tags": tags,
        "similar_artists": similar
    }


def fetch_top_brazil_artists():
    top_artists = get_top_artists_brazil()
    final_data = []

    for artist in top_artists:
        try:
            info = get_artist_info(artist["name"])

            normalized_tags = [t.lower().strip() for t in info["tags"]]

            final_data.append({
                "rank": artist["rank"],
                "artist_name": artist["name"],
                "mbid": artist["mbid"],
                "lastfm_url": artist["lastfm_url"],
                "listeners_brazil": artist["listeners_brazil"],
                "listeners_global": info["listeners_global"],
                "playcount_global": info["playcount_global"],
                "ontour": info["ontour"],
                "tags": info["tags"],
                "similar_artists": info["similar_artists"],
                "extracted_at": datetime.now().isoformat()
            })
            logger.info(f"#{artist['rank']} {artist['name']} extraído.")

        except Exception as e:
            logger.error(f"Erro ao processar {artist['name']}: {str(e)}")

    if final_data:
        os.makedirs(RAW_PATH, exist_ok=True)
        filename = f"{RAW_PATH}/top10_brazil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Dados salvos em {filename}")
    else:
        raise ValueError(
            "Nenhum dado capturado. Verifique a API key e conexões.")


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="top10_brazil_artists",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False
) as dag:

    fetch_data = PythonOperator(
        task_id="fetch_top_brazil_artists",
        python_callable=fetch_top_brazil_artists,
    )

    load_to_duckdb = BashOperator(
        task_id="load_to_duckdb",
        bash_command="python /opt/airflow/dags/scripts/load_lastfm.py 2>&1",
    )

    fetch_data >> load_to_duckdb
