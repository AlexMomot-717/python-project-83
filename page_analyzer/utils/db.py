import os
from typing import Any, Dict, List

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from page_analyzer.utils.url import check_url

load_dotenv()


def connect_db() -> Any:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn


def get_url_data(url_id: int) -> Dict[str, int | str] | None:
    conn = connect_db()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as dict_cur:
        dict_cur.execute(
            "SELECT * FROM urls WHERE id=%(int)s;",
            {
                "int": url_id,
            },
        )
        target_url_data: dict[str, int | str] | None = dict_cur.fetchone()
        if not target_url_data:
            conn.close()
            return None
    conn.close()
    return target_url_data


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


def get_urls() -> List[Dict[str, Any]]:
    conn = connect_db()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as dict_cur:
        dict_cur.execute(
            "SELECT DISTINCT ON (u.id)"
            " u.id AS url_id,"
            " u.name AS url_name,"
            " COALESCE(c.created_at::varchar, '') AS created_at,"
            " COALESCE(c.status_code::varchar, '') AS status_code"
            " FROM urls u"
            " LEFT JOIN checks c"
            " ON c.url_id = u.id"
            " ORDER BY u.id DESC, c.created_at DESC;"
        )
        urls_data_list = dict_cur.fetchall()
    conn.close()
    actual_urls_data = []
    for url_data in urls_data_list:
        actual_urls_data.append(url_data)
    return actual_urls_data


def create_check(url_data: Dict[str, Any]) -> bool:
    check_result = check_url(str(url_data["name"]))
    if check_result is None:
        return False
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO checks"
            " (url_id, status_code, h1, title, description)"
            " VALUES (%s, %s, %s, %s, %s);",
            (
                url_data["id"],
                check_result["response_code"],
                check_result["h1"],
                check_result["title"],
                check_result["description"],
            ),
        )
        conn.commit()
    conn.close()
    return True


def get_url_checks(url_id: int) -> List[Dict[str, str]]:
    conn = connect_db()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as dict_cur:
        dict_cur.execute(
            "SELECT * FROM checks WHERE url_id=%(int)s ORDER BY id DESC;",
            {
                "int": url_id,
            },
        )
        url_checks = dict_cur.fetchall()
    conn.close()
    actual_checks_data = []
    for check_data in url_checks:
        actual_checks_data.append(dict(check_data))
    return actual_checks_data
