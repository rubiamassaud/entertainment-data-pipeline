WITH raw_source AS (
    -- Lendo da tabela que o seu script load_movies.py criou
    SELECT * FROM {{ source('raw_data', 'raw_movies_json') }}
),

flattened_results AS (
    -- O unnest transforma cada item da lista 'results' em uma linha individual
    SELECT unnest(results) AS movie_data FROM raw_source
)

SELECT
    -- Usamos o operador ->> para extrair valores do objeto JSON
    (movie_data->>'id')::INTEGER AS movie_id,
    movie_data->>'title' AS title,
    movie_data->>'original_title' AS original_title,
    (movie_data->>'release_date')::DATE AS release_date,
    (movie_data->>'popularity')::DOUBLE AS popularity,
    (movie_data->>'vote_average')::DOUBLE AS vote_average,
    (movie_data->>'vote_count')::INTEGER AS vote_count,
    movie_data->>'overview' AS overview,
    movie_data->>'poster_path' AS poster_url
FROM flattened_results