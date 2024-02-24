from unittest.mock import MagicMock, patch

import requests
from page_analyzer.utils.url import (
    check_url,
    normalize,
    parse_page_data,
    validate,
)


def test_validate():
    # given
    url = "https://www.weforum.org/my-forum/"

    # when
    errors = validate(url)

    # then
    assert errors == {}


def test_validate_invalid():
    # given
    url = "htttps://www.weforum.org/my-forum/"

    # when
    errors = validate(url)

    # then
    assert errors == {"name": "Некорректный URL"}


def test_normalize():
    # given
    url = "http://www.example.com:1030/software/index.html"

    # when
    normalized_url = normalize(url)

    # then
    assert normalized_url == "http://www.example.com"


def test_check_url():
    # given
    url = "https://example.com"

    request_response_mock = MagicMock()
    request_response_mock.status_code = 200
    request_response_mock.content = (
        "<title>some title</title>"
        "<meta name='description' content='some description'></meta>"
        "<h1>some header</h1>"
    )

    # when
    with patch(
        "page_analyzer.utils.url.requests.get", return_value=request_response_mock
    ) as mock_requests:
        check_result = check_url(url)

    # then
    mock_requests.assert_called_once_with(url)
    assert check_result == {
        "response_code": "200",
        "h1": "some header",
        "title": "some title",
        "description": "some description",
    }


def test_check_url_exception():
    # given
    url = "http://www.fake.com"

    # when
    with patch(
        "page_analyzer.utils.url.requests.get",
        side_effect=requests.exceptions.RequestException,
    ) as mock_requests:
        check_result = check_url(url)

    # then
    mock_requests.assert_called_once_with(url)
    assert check_result is None


def test_check_url_unavailable():
    # given
    url = "http://www.unavailable.com"

    request_response_mock = MagicMock()
    request_response_mock.status_code = 404

    # when
    with patch(
        "page_analyzer.utils.url.requests.get", return_value=request_response_mock
    ) as mock_requests:
        check_result = check_url(url)

    # then
    mock_requests.assert_called_once_with(url)
    assert check_result is None


def test_parse_page_data():
    html_content = (
        "<title>title</title>"
        "<meta name='description' content='description'></meta>"
        "<h1>header</h1>"
    )
    request_response_mock = MagicMock()
    request_response_mock.content = html_content

    # when
    page_data = parse_page_data(request_response_mock)

    # then
    assert page_data == {
        "response_code": "200",
        "h1": "header",
        "title": "title",
        "description": "description",
    }


def test_parse_page_data_no_description():
    # given
    html_content = "<title>title</title><h1>header</h1>"

    request_response_mock = MagicMock()
    request_response_mock.content = html_content

    # when
    page_data = parse_page_data(request_response_mock)

    # then
    assert page_data == {
        "response_code": "200",
        "h1": "header",
        "title": "title",
        "description": "",
    }
