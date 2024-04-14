from datetime import date
from unittest.mock import patch

from freezegun import freeze_time
from page_analyzer.utils.db import (
    create_check,
    create_url,
    get_url_by_name,
    get_url_checks,
    get_url_data,
    get_urls,
)


@freeze_time("2024-05-01")
def test_create_url(test_database: None) -> None:
    # given
    url_name = "https://example.com"

    # when
    url_id = create_url(url_name)

    # then
    created_url = get_url_data(url_id)
    assert created_url == {
        "id": 1,
        "name": "https://example.com",
        "created_at": date.today(),
    }


@freeze_time("2024-05-01")
def test_get_url_data(test_database: None) -> None:
    # given
    url_name = "https://example.com"

    url_id = create_url(url_name)

    # when
    url_data_result = get_url_data(url_id)

    # then
    assert url_data_result == {
        "id": 1,
        "name": "https://example.com",
        "created_at": date.today(),
    }


def test_get_url_data_none(test_database: None) -> None:
    # given
    url_id = -1

    # when
    url_data_result = get_url_data(url_id)

    # then
    assert url_data_result is None


def test_get_url_by_name(test_database: None) -> None:
    # given
    url_name = "https://example.com"
    url_id = create_url(url_name)

    # when
    found_url_id = get_url_by_name(url_name)

    # then
    assert found_url_id == url_id


def test_get_url_by_name_none(test_database: None) -> None:
    # given
    url_name = "https://example.com"

    # when
    url_id = get_url_by_name(url_name)

    # then
    assert url_id is None


def test_get_urls(test_database: None) -> None:
    # given (no checks in DB)
    url_name1 = "https://example1.com"
    url_name2 = "https://example2.com"

    create_url(url_name1)
    create_url(url_name2)

    # when
    urls_data = get_urls()

    # then (latest urls should go first)
    assert urls_data == [
        {
            "url_id": 2,
            "url_name": "https://example2.com",
            "created_at": "",
            "status_code": "",
        },
        {
            "url_id": 1,
            "url_name": "https://example1.com",
            "created_at": "",
            "status_code": "",
        },
    ]


def test_get_urls_empty(test_database: None) -> None:
    # given (no urls in DB)

    # when
    urls_data = get_urls()

    # then
    assert urls_data == []


@freeze_time("2024-05-01")
def test_create_check(test_database: None) -> None:
    # given
    url_name = "https://example.com"

    url_id = create_url(url_name)
    url_data = get_url_data(url_id)
    assert url_data is not None

    # when
    with patch(
        "page_analyzer.utils.db.check_url",
        return_value={
            "response_code": "200",
            "h1": "some header",
            "title": "some title",
            "description": "some description",
        },
    ) as mock_check_url:
        check_success_status = create_check(url_data)

    # then
    mock_check_url.assert_called_once_with("https://example.com")
    assert check_success_status is True
    assert get_url_checks(url_id) == [
        {
            "id": 1,
            "url_id": 1,
            "status_code": 200,
            "h1": "some header",
            "title": "some title",
            "description": "some description",
            "created_at": date.today(),
        },
    ]


def test_create_check_false(test_database: None) -> None:
    # given
    url_name = "https://example.com"

    url_id = create_url(url_name)
    url_data = get_url_data(url_id)
    assert url_data is not None

    # when
    with patch(
        "page_analyzer.utils.db.check_url",
        return_value=None,
    ) as mock_check_url:
        check_success_status = create_check(url_data)

    # then
    mock_check_url.assert_called_once_with(url_name)
    assert check_success_status is False
    assert get_url_checks(url_id) == []


@freeze_time("2024-05-01")
def test_get_url_checks(test_database: None) -> None:
    # given
    url_name = "https://example.com"
    url_id = create_url(url_name)
    url_data = get_url_data(url_id)
    assert url_data is not None

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
        create_check(url_data)

    # when
    urls_checks_data = get_url_checks(url_id)

    # then
    assert urls_checks_data == [
        {
            "id": 1,
            "url_id": 1,
            "status_code": 200,
            "h1": "some header",
            "title": "some title",
            "description": "some description",
            "created_at": date.today(),
        },
    ]


def test_get_url_checks_empty(test_database: None) -> None:
    # given
    url_id = 1

    # when
    urls_checks_data = get_url_checks(url_id)

    # then
    assert urls_checks_data == []
