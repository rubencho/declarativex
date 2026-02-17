import json
import time
from json import JSONDecodeError

import httpx
import pytest

from declarativex.exceptions import (
    DependencyValidationError,
)
from .fixtures import (
    async_dataclass_client,
    async_pydantic_client,
    async_dictionary_client,
    dataclass,
    pydantic,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type",
    [
        (async_dataclass_client, dataclass.User),
        (async_pydantic_client, pydantic.User),
        (async_dictionary_client, dict),
    ],
)
async def test_async_get_user(client, response_type):
    user = await client.get_user(1)
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert user.get("id") == 1
    else:
        assert user.id == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,item_type",
    [
        (async_dataclass_client, dataclass.User),
        (async_pydantic_client, pydantic.User),
        (async_dictionary_client, dict),
    ],
)
async def test_async_get_users(client, item_type):
    users = await client.get_users()
    assert isinstance(users, list)
    assert len(users) == 10
    assert isinstance(users[0], item_type)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,body,response_type",
    [
        (
            async_dataclass_client,
            dataclass.BaseUserSchema(name="John", job="worker"),
            dataclass.UserCreateResponse,
        ),
        (
            async_pydantic_client,
            pydantic.BaseUserSchema(name="John", job="worker"),
            pydantic.UserCreateResponse,
        ),
        (async_dictionary_client, dict(name="John", job="worker"), dict),
        (
            async_dictionary_client,
            json.dumps({"name": "John", "job": "worker"}),
            dict,
        ),
    ],
)
async def test_async_create_user(client, body, response_type):
    import asyncio

    user = await client.create_user(user=body)
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert "id" in user
    else:
        assert user.id

    await asyncio.sleep(1.5)

    if response_type is dict:
        with pytest.raises(DependencyValidationError) as err:
            _ = await client.create_user(user="invalid json")

        assert isinstance(err.value.__cause__, JSONDecodeError)

    await asyncio.sleep(1.5)

    start_time = time.perf_counter()
    for i in range(3):
        await client.create_user(user=body)
    elapsed = time.perf_counter() - start_time
    assert elapsed > 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type",
    [
        (async_dataclass_client, dataclass.UserUpdateResponse),
        (async_pydantic_client, pydantic.UserUpdateResponse),
        (async_dictionary_client, dict),
    ],
)
async def test_async_update_user(client, response_type):
    user = await client.update_user(user_id=1, name="John", job="worker")
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert "name" in user and "job" in user
    else:
        assert user.name and user.job


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client",
    [
        async_dataclass_client,
        async_pydantic_client,
        async_dictionary_client,
    ],
)
async def test_async_delete_user(client):
    response = await client.delete_user(1)
    assert isinstance(response, httpx.Response)
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client",
    [
        async_dataclass_client,
        async_pydantic_client,
        async_dictionary_client,
    ],
)
async def test_async_delete_user_type_hinted_method(client):
    response = await client.delete_user_explicit_typehint(1)
    assert isinstance(response, httpx.Response)
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,item_type",
    [
        (async_dataclass_client, dataclass.Post),
        (async_pydantic_client, pydantic.Post),
        (async_dictionary_client, dict),
    ],
)
async def test_async_get_posts_list(
    client, item_type
):
    posts = await client.get_posts_by_resource()
    assert isinstance(posts, list)
    assert len(posts) == 100
    assert isinstance(posts[0], item_type)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "client,response_type",
    [
        (async_dataclass_client, dataclass.Post),
        (async_pydantic_client, pydantic.Post),
        (async_dictionary_client, dict),
    ],
)
async def test_async_get_post(
    client, response_type
):
    post = await client.get_post(1)
    assert isinstance(post, response_type)
    if isinstance(post, dict):
        assert post.get("id") == 1
    else:
        assert post.id == 1
