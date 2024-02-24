from typing import Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
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


def check_url(url: str) -> Dict[str, str] | None:
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        return None
    status_code = r.status_code
    if status_code != 200:
        return None
    return parse_page_data(r)


def parse_page_data(r: requests.models.Response) -> Dict[str, str]:
    html = BeautifulSoup(r.content, "html.parser")
    h1_el = html.find("h1")
    h1 = "" if not h1_el else h1_el.get_text()
    title_el = html.find("title")
    title = "" if not title_el else title_el.get_text()
    tags = html.find_all("meta", {"name": "description"})
    if not tags:
        description = ""
    else:
        description = tags[0].get("content", "")
    return {
        "response_code": "200",
        "h1": h1,
        "title": title,
        "description": description,
    }
