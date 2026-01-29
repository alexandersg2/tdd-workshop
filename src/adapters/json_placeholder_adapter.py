import requests
from pydantic import BaseModel, ValidationError

from adapters.exceptions import FailedToFetchPostsError
from domain.exceptions import InvalidPostError

# * Faking an env variable - demo purposes only
BASE_URL_ENV = "https://jsonplaceholder.typicode.com"


class Post(BaseModel):
    id: int
    title: str


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

    # TODO: Implement get_post(post_id: int) method

    # TODO: Implement get_comments(post_id: int) method
