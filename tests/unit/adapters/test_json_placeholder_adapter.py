from unittest.mock import patch

import pytest
import requests

from adapters.exceptions import FailedToFetchPostsError
from adapters.json_placeholder_adapter import BASE_URL_ENV, JsonPlaceholderAdapter, Post
from domain.exceptions import InvalidPostError


class TestInit:
    def test_init(self):
        adapter = JsonPlaceholderAdapter()
        assert adapter.base_url == BASE_URL_ENV


class TestGetPosts:
    @patch("src.adapters.json_placeholder_adapter.requests.get")
    def test_returns_posts(self, mock_get):
        mock_get.return_value.json.return_value = [
            {"id": 1, "title": "Test Post", "body": "Test Body"}
        ]
        adapter = JsonPlaceholderAdapter()

        posts = adapter.get_posts()

        assert posts == [
            Post(
                id=1,
                title="Test Post",
            )
        ]

    @patch("src.adapters.json_placeholder_adapter.requests.get")
    def test_raises_error_when_request_fails(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException(
            "Internal Server Error"
        )
        adapter = JsonPlaceholderAdapter()

        with pytest.raises(FailedToFetchPostsError):
            adapter.get_posts()
    
    @patch("src.adapters.json_placeholder_adapter.requests.get")
    def test_returns_error_on_error_response_code(self, requests_mock):
        requests_mock.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError

        client = JsonPlaceholderAdapter()

        with pytest.raises(FailedToFetchPostsError):
            client.get_posts()

    @patch("src.adapters.json_placeholder_adapter.requests.get")
    def test_raises_error_when_response_is_invalid(self, mock_get):
        mock_get.return_value.json.return_value = [{"id": 1}]
        adapter = JsonPlaceholderAdapter()

        with pytest.raises(InvalidPostError):
            adapter.get_posts()
