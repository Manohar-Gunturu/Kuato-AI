import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from python.downloader import Resource

class WebPageResource(Resource):
    def __init__(self):
        pass

    def download(self, path: str) -> tuple[str, str]:
        try:
            resp = requests.get(path, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            return (path, text)
        except Exception:
            return (path, "")