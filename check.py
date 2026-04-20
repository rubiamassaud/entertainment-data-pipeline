import duckdb
con = duckdb.connect('data/entertainment.duckdb')
print(con.execute(
    "SELECT * FROM read_json_auto('data/raw/lastfm_*.json') LIMIT 1").df().to_string())
import duckdb
con = duckdb.connect('data/entertainment.duckdb')
print(con.execute('SELECT * FROM "stg.lastfm" LIMIT 5').df())