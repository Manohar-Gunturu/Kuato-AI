from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict

from python.downloader.Resource import Resource
from python.downloader.WebPageResource import WebPageResource
from python.downloader.LocalTextFileResource import LocalTextFileResource
from python.downloader.LocalPDFFileResource import LocalPDFFileResource


class ResourceFactory:
    _instances: Dict[str, Resource] = {}

    @classmethod
    def _get_instance(cls, key: str) -> Resource:
        if key in cls._instances:
            return cls._instances[key]

        if key == "web":
            cls._instances[key] = WebPageResource()
        elif key == "pdf":
            cls._instances[key] = LocalPDFFileResource()
        elif key == "text":
            cls._instances[key] = LocalTextFileResource()
        else:
            # Default to text
            cls._instances[key] = LocalTextFileResource()
        return cls._instances[key]

    @classmethod
    def get_for_path(cls, path: str) -> Resource:
        parsed = urlparse(path)
        if parsed.scheme in ("http", "https"):
            return cls._get_instance("web")

        suffix = Path(path).suffix.lower()
        if suffix == ".pdf":
            return cls._get_instance("pdf")

        # Treat common text/code/doc formats as text; default to text otherwise
        if suffix in {".txt", ".rtf", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".csv", ".log"}:
            return cls._get_instance("text")

        return cls._get_instance("text")