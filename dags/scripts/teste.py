import requests
import json

LASTFM_URL = "https://ws.audioscrobbler.com/2.0/"
LASTFM_API_KEY = "2773414e8f50eb6711c3c839d4344e82"

response = requests.get(LASTFM_URL, params={
    "method": "artist.getinfo",
    "artist": "Sabrina Carpenter",
    "api_key": LASTFM_API_KEY,
    "format": "json"
})
print(json.dumps(response.json(), indent=2))