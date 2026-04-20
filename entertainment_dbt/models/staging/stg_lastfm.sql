/*
  Mestra, aqui fazemos o casting final.
  O DuckDB já leu o JSON, o dbt agora oficializa os tipos.
*/

WITH raw_source AS (
    -- 'raw_data' é o nome do source e 'top10_brazil_artists' a tabela do Python
    SELECT * FROM {{ source('raw_data', 'top10_brazil_artists') }}
)

SELECT
    (rank)::INTEGER AS ranking,
    artist_name,
    mbid,
    lastfm_url,
    (listeners_brazil)::INTEGER AS listeners_brazil,
    (listeners_global)::INTEGER AS listeners_global,
    (playcount_global)::BIGINT AS playcount_global, -- BIGINT para números gigantes
    ontour::BOOLEAN AS is_on_tour,
    -- Converte a lista de tags em uma string amigável para o dashboard
    array_to_string(tags, ', ') AS genres,
    (extracted_at)::TIMESTAMP AS data_extracao
FROM raw_source