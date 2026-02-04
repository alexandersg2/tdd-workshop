from unittest import TestCase
from unittest.mock import patch

import pytest
import requests

from adapters.exceptions import FailedToFetchPostsError, FailedToFetchPostError, FailedToFetchCommentsError
from adapters.json_placeholder_adapter import BASE_URL_ENV, JsonPlaceholderAdapter, Post, Comment
from domain.exceptions import InvalidPostError, InvalidCommentError


class TestInit:
    def test_init(self):
        adapter = JsonPlaceholderAdapter()
        assert adapter.base_url == BASE_URL_ENV


class TestGetPosts:
    @patch("adapters.json_placeholder_adapter.requests.get")
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

    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_raises_error_when_request_fails(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException(
            "Internal Server Error"
        )
        adapter = JsonPlaceholderAdapter()

        with pytest.raises(FailedToFetchPostsError):
            adapter.get_posts()
    
    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_returns_error_on_error_response_code(self, requests_mock):
        requests_mock.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError

        client = JsonPlaceholderAdapter()

        with pytest.raises(FailedToFetchPostsError):
            client.get_posts()

    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_raises_error_when_response_is_invalid(self, mock_get):
        mock_get.return_value.json.return_value = [{"id": 1}]
        adapter = JsonPlaceholderAdapter()

        with pytest.raises(InvalidPostError):
            adapter.get_posts()

class TestGetPost(TestCase):
    def setUp(self):
        self.adapter = JsonPlaceholderAdapter()

    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_get_post(self, mock_get):
        mock_get.return_value.json.return_value = {"id": 1, "title": "Test Post", "body": "Test Body"}
        assert self.adapter.get_post(1) == Post(**{"id": 1, "title": "Test Post"})

    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_get_post_with_invalid_id(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError
        with pytest.raises(FailedToFetchPostError):
            self.adapter.get_post(1)

    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_get_post_with_invalid_post_data(self, mock_get):
        mock_get.return_value.json.return_value = {"id": 1}
        with pytest.raises(InvalidPostError):
            self.adapter.get_post(1)

class TestGetComments(TestCase):
    def setUp(self):
        self.adapter = JsonPlaceholderAdapter()
        self.mock_data = [{"id": 1, "postId": 1, "body": "Test Body"}]

    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_get_comments(self, mock_get):
        mock_get.return_value.json.return_value = self.mock_data
        comments = self.adapter.get_comments(1)
        assert len(comments) == 1
        assert comments[0] == Comment(**self.mock_data[0])

    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_get_comments_with_invalid_id(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError
        with pytest.raises(FailedToFetchCommentsError):
            self.adapter.get_comments(1)

    @patch("adapters.json_placeholder_adapter.requests.get")
    def test_get_comments_with_invalid_post_data(self, mock_get):
        mock_get.return_value.json.return_value = [{"id": 1}]
        with pytest.raises(InvalidCommentError):
            self.adapter.get_comments(1)