from typing import Annotated, List
from typing import Union

import httpx

from declarativex import (
    BaseClient,
    JsonField,
    rate_limiter,
    Json,
    Path,
    Timeout,
    Query,
    http,
)
from tests.fixtures.schemas import dataclass, pydantic

async_dataclass_client = None
async_pydantic_client = None
async_dictionary_client = None


for schema in [dataclass, pydantic, None]:
    UserResponseSchema = schema.User if schema else dict
    UserListResponseSchema = List[schema.User] if schema else List[dict]
    CreateUserSchema = schema.BaseUserSchema if schema else Union[dict, str]
    CreateUserResponseSchema = schema.UserCreateResponse if schema else dict
    UpdateUserResponseSchema = schema.UserUpdateResponse if schema else dict
    PostListResponseSchema = List[schema.Post] if schema else List[dict]
    PostResponseSchema = schema.Post if schema else dict

    class AsyncClientPydantic(BaseClient):
        base_url = "https://jsonplaceholder.typicode.com/"

        @http("GET", "users/{user_id}")
        async def get_user(
            self,
            user_id: Annotated[int, Path],
            timeout: Annotated[float, Timeout()] = 2.0,
        ) -> UserResponseSchema:
            ...

        @http("GET", "users", timeout=2)
        async def get_users(self) -> UserListResponseSchema:
            ...

        @rate_limiter(max_calls=1, interval=1)
        @http("POST", "users")
        async def create_user(
            self,
            user: Annotated[CreateUserSchema, Json()],
        ) -> CreateUserResponseSchema:
            ...

        @http("PUT", "users/{user_id}")
        async def update_user(
            self,
            user_id: int,
            name: Annotated[str, JsonField()],
            job: Annotated[str, JsonField()],
        ) -> UpdateUserResponseSchema:
            ...

        @http("DELETE", "users/{user_id}")
        async def delete_user(self, user_id: int):
            ...

        @http("DELETE", "users/{user_id}")
        async def delete_user_explicit_typehint(
            self, user_id: int
        ) -> httpx.Response:
            ...

        @http("GET", "{resource}")
        async def get_posts_by_resource(
            self,
            resource_name: Annotated[
                str, Path(field_name="resource")
            ] = "posts",
        ) -> PostListResponseSchema:
            ...

        @http("GET", "posts/{post_id}")
        async def get_post(
            self, post_id: int
        ) -> PostResponseSchema:
            ...

    if schema == dataclass:
        async_dataclass_client = AsyncClientPydantic()
    elif schema == pydantic:
        async_pydantic_client = AsyncClientPydantic()
    elif schema is None:
        async_dictionary_client = AsyncClientPydantic()
