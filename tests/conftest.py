import os
from typing import Generator

import pytest
from flask.testing import FlaskClient
from page_analyzer.app import app as test_app
from page_analyzer.utils.db import connect_db


@pytest.fixture
def client() -> FlaskClient:
    test_app.config.update(
        {
            "TESTING": True,
        }
    )
    test_app.secret_key = "dummy-secret-key"
    return test_app.test_client()


@pytest.fixture
def test_database() -> Generator[None, None, None]:
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
