import requests


class GiphyClient:
    BASE_URL = "https://api.giphy.com/v1/gifs/search"

    def __init__(self, api_key: str):
        self._api_key = api_key

    def search(self, query: str, limit: int = 1) -> str | None:
        """Returns URL of the first found GIF, or None."""
        params = {
            "api_key": self._api_key,
            "q": query,
            "limit": limit,
            "rating": "pg-13",
            "lang": "en"
        }
        response = requests.get(self.BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        gifs = data.get("data", [])
        if not gifs:
            return None

        return gifs[0]["images"]["original"]["url"]
