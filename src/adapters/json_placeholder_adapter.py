import requests
from pydantic import BaseModel, ValidationError

from adapters.exceptions import FailedToFetchPostsError, FailedToFetchPostError, FailedToFetchCommentsError
from domain.exceptions import InvalidPostError, InvalidCommentError

# * Faking an env variable - demo purposes only
BASE_URL_ENV = "https://jsonplaceholder.typicode.com"


class Post(BaseModel):
    id: int
    title: str

class Comment(BaseModel):
    id: int
    postId: int
    body: str


class JsonPlaceholderAdapter:
    def __init__(self) -> None:
        self.base_url = BASE_URL_ENV

    def get_posts(self) -> list[Post]:
        try:
            response = requests.get(f"{self.base_url}/posts")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise FailedToFetchPostsError(f"Failed to fetch posts: {e}") from e

        try:
            posts = [Post(**post) for post in response.json()]
        except ValidationError as e:
            raise InvalidPostError() from e

        return posts

    def get_post(self, post_id: int) -> Post:
        try:
            response = requests.get(f"{self.base_url}/posts/{post_id}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise FailedToFetchPostError(f"Failed to fetch post: {e}") from e

        try:
            return Post(**response.json())
        except ValidationError as e:
            raise InvalidPostError() from e

    def get_comments(self, post_id: int) -> list[Comment]:
        try:
            response = requests.get(f"{self.base_url}/posts/{post_id}/comments")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise FailedToFetchCommentsError(f"Failed to fetch comments: {e}") from e

        try:
            return [Comment(**comment) for comment in response.json()]
        except ValidationError as e:
            raise InvalidCommentError() from e


