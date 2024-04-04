import os

import pytest
from page_analyzer.utils.db import connect_db


@pytest.fixture
def test_database():
    """
    Makes tests to use test database

    On setup: sets environment variable "DATABASE_URL" for test database

    On teardown: cleans test database
    """
    os.environ[
        "DATABASE_URL"
    ] = "postgresql://page-analyzer:page-analyzer@localhost:5432/page-analyzer"
    yield
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE urls RESTART IDENTITY CASCADE;")
    conn.commit()
    conn.close()
