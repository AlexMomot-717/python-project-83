import datetime
from unittest.mock import patch

from flask.testing import FlaskClient
from freezegun import freeze_time
from page_analyzer.utils.db import (
    create_check,
    create_url,
    get_url_by_name,
    get_url_checks,
    get_url_data,
)
from tests.paths import resolve_path


def test_index(client: FlaskClient) -> None:
    # given
    route = "/"

    # when
    response = client.get(route)

    # then
    expected_html = resolve_path("fixtures/expected_index.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200


@freeze_time("2024-05-01")
def test_add_url(client: FlaskClient, test_database: None) -> None:
    # given
    url_name = "https://www.example.com"
    route = "/urls"

    # when
    response = client.post(route, data={"url": url_name}, follow_redirects=True)

    # then
    expected_html = resolve_path("fixtures/expected_url_add.html")
    assert response.data == expected_html.read_bytes()
    assert get_url_by_name(url_name) == 1
    assert response.status_code == 200


@freeze_time("2024-05-01")
def test_add_url_exists(client: FlaskClient, test_database: None) -> None:
    # given
    url_name = "https://www.example.com"
    create_url(url_name)
    route = "/urls"

    # when
    response = client.post(route, data={"url": url_name}, follow_redirects=True)

    # then
    expected_html = resolve_path("fixtures/expected_url_exists.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200


def test_add_url_error(client: FlaskClient, test_database: None) -> None:
    # given
    url_name = "htttps://www.example.com"
    route = "/urls"

    # when
    response = client.post(route, data={"url": url_name}, follow_redirects=True)

    # then
    expected_html = resolve_path("fixtures/expected_index_incorrect_url.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 422


@freeze_time("2024-05-01")
def test_show_url(client: FlaskClient, test_database: None) -> None:
    # given (no given url checks in DB)
    url_name = "https://www.example.com"
    url_id = create_url(url_name)
    route = f"/urls/{url_id}"

    # when
    response = client.get(route)

    # then
    expected_html = resolve_path("fixtures/expected_url.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200


@freeze_time("2024-05-01")
def test_show_url_with_checks(client: FlaskClient, test_database: None) -> None:
    # given
    url_name = "https://www.example.com"
    url_id = create_url(url_name)
    url_data = get_url_data(url_id)
    assert url_data is not None
    route = f"/urls/{url_id}"

    with patch(
        "page_analyzer.utils.db.check_url",
        return_value={
            "response_code": "200",
            "h1": "some header",
            "title": "some title",
            "description": "some description",
        },
    ):
        create_check(url_data)

    # when
    response = client.get(route)

    # then
    expected_html = resolve_path("fixtures/expected_url_with_checks.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200


def test_show_url_none(client: FlaskClient, test_database: None) -> None:
    # given
    url_id = 0
    route = f"/urls/{url_id}"

    # when
    response = client.get(route)

    # then
    expected_html = resolve_path("fixtures/expected_page_not_found.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200


@freeze_time("2024-05-01")
def test_list_urls(client: FlaskClient, test_database: None) -> None:
    # given
    url_name = "https://www.example.com"
    url_id = create_url(url_name)
    url_data = get_url_data(url_id)
    assert url_data is not None
    route = "/urls"

    with patch(
        "page_analyzer.utils.db.check_url",
        return_value={
            "response_code": "200",
            "h1": "",
            "title": "",
            "description": "",
        },
    ):
        create_check(url_data)

    # when
    response = client.get(route)

    # then
    expected_html = resolve_path("fixtures/expected_urls.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200


def test_list_urls_empty(client: FlaskClient, test_database: None) -> None:
    # given (no urls in DB)
    route = "/urls"

    # when
    response = client.get(route)

    # then
    expected_html = resolve_path("fixtures/expected_urls_empty.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200


@freeze_time("2024-05-01")
def test_add_url_check(client: FlaskClient, test_database: None) -> None:
    # given
    url_name = "https://www.example1.com"
    url_id = create_url(url_name)
    route = f"/urls/{url_id}/checks"

    # when
    with patch(
        "page_analyzer.utils.db.check_url",
        return_value={
            "response_code": "200",
            "h1": "some header",
            "title": "some title",
            "description": "some description",
        },
    ):
        response = client.post(route, follow_redirects=True)

    # then
    expected_html = resolve_path("fixtures/expected_url_checks_add.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200
    url_found_checks_data = get_url_checks(url_id)
    assert url_found_checks_data == [
        {
            "id": 1,
            "url_id": 1,
            "status_code": 200,
            "h1": "some header",
            "title": "some title",
            "description": "some description",
            "created_at": datetime.date(2024, 5, 1),
        }
    ]


@freeze_time("2024-05-01")
def test_add_url_check_fails(client: FlaskClient, test_database: None) -> None:
    # given
    url_name = "https://www.example1.com"
    url_id = create_url(url_name)
    route = f"/urls/{url_id}/checks"

    # when
    with patch("page_analyzer.utils.db.check_url", return_value=None):
        response = client.post(route, follow_redirects=True)

    # then
    expected_html = resolve_path("fixtures/expected_url_check_fails.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200
    url_found_checks_data = get_url_checks(url_id)
    assert url_found_checks_data == []


def test_add_url_check_no_url(client: FlaskClient, test_database: None) -> None:
    # given
    url_id = 99
    route = f"/urls/{url_id}/checks"

    # when
    response = client.post(route, follow_redirects=True)

    # then
    expected_html = resolve_path("fixtures/expected_page_not_found.html")
    assert response.data == expected_html.read_bytes()
    assert response.status_code == 200
    url_found_checks_data = get_url_checks(url_id)
    assert url_found_checks_data == []
