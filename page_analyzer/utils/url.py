from typing import Dict
from urllib.parse import urlparse

from validators import url


def validate(url_name: str) -> Dict[str, str]:
    errors = {}
    if not url(url_name) or len(url_name) > 255:
        errors["name"] = "Некорректный URL"
    return errors


def normalize(url_name: str) -> str:
    p = urlparse(url_name)
    normalized = p.scheme + "://" + p.netloc
    if p.port:
        port = ":" + str(p.port)
        normalized = normalized.replace(port, "")
    return normalized
