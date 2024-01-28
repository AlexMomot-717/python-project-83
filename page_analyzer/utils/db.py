import os
from typing import Any, List

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def connect_db() -> Any:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn


def get_url_context(url_id: int) -> dict[str, int | str] | None:
    conn = connect_db()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as dict_cur:
        dict_cur.execute(
            "SELECT * FROM urls WHERE id=%(int)s;",
            {
                "int": url_id,
            },
        )
        target_url_data = dict_cur.fetchone()
        if target_url_data:
            conn.close()
            actual_url_data: dict[str, int | str] = {
                "id": url_id,
                "name": str(target_url_data["name"]),
                "created_at": str(target_url_data["created_at"]),
            }
            return actual_url_data
    conn.close()
    return None


def get_url_by_name(url_name: str) -> int | None:
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM urls WHERE name=%(str)s;",
            {
                "str": url_name,
            },
        )
        target_url_id = cur.fetchone()
        if target_url_id:
            url_id = target_url_id[0]
            conn.close()
            return int(url_id)
    conn.close()
    return None


def create_url(url_name: str) -> int:
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO urls (name) VALUES (%(str)s) RETURNING id;",
            {
                "str": url_name,
            },
        )
        url_id = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return int(url_id)


def get_urls_data() -> List[int | str]:
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls ORDER BY id DESC;")
        urls_data_list = cur.fetchall()
    conn.close()
    return list(urls_data_list)
