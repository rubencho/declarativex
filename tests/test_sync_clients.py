import json
import time
from json import JSONDecodeError
from typing import Annotated
from unittest.mock import Mock, MagicMock

import httpx
import pytest
from httpx import Response, Proxy, URL
from pytest_mock import MockerFixture

from declarativex import http, BaseClient
from declarativex.dependencies import Files
from declarativex.exceptions import (
    DependencyValidationError,
    TimeoutException,
)
from .fixtures import (
    sync_dataclass_client,
    sync_pydantic_client,
    sync_dictionary_client,
    dataclass,
    pydantic,
)


@pytest.mark.parametrize(
    "client,response_type",
    [
        (sync_dataclass_client, dataclass.User),
        (sync_pydantic_client, pydantic.User),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_get_user(client, response_type):
    user = client.get_user(1)
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert user.get("id") == 1
    else:
        assert user.id == 1


@pytest.mark.parametrize(
    "client,item_type",
    [
        (sync_dataclass_client, dataclass.User),
        (sync_pydantic_client, pydantic.User),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_get_users(client, item_type):
    users = client.get_users()
    assert isinstance(users, list)
    assert len(users) == 10
    assert isinstance(users[0], item_type)


@pytest.mark.parametrize(
    "client,body,response_type",
    [
        (
            sync_dataclass_client,
            dataclass.BaseUserSchema(name="John", job="worker"),
            dataclass.UserCreateResponse,
        ),
        (
            sync_pydantic_client,
            pydantic.BaseUserSchema(name="John", job="worker"),
            pydantic.UserCreateResponse,
        ),
        (sync_dictionary_client, dict(name="John", job="worker"), dict),
        (
            sync_dictionary_client,
            json.dumps({"name": "John", "job": "worker"}),
            dict,
        ),
    ],
)
def test_sync_create_user(client, body, response_type):
    user = client.create_user(user=body)
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert "id" in user
    else:
        assert user.id

    time.sleep(1.5)

    if response_type is dict:
        with pytest.raises(DependencyValidationError) as err:
            _ = client.create_user(user="invalid json")

        assert isinstance(err.value.__cause__, JSONDecodeError)

    time.sleep(1.5)

    start_time = time.perf_counter()
    for i in range(3):
        client.create_user(user=body)
    elapsed = time.perf_counter() - start_time
    assert elapsed > 2


@pytest.mark.parametrize(
    "client,response_type",
    [
        (sync_dataclass_client, dataclass.UserUpdateResponse),
        (sync_pydantic_client, pydantic.UserUpdateResponse),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_update_user(client, response_type):
    user = client.update_user(user_id=1, name="John", job="worker")
    assert isinstance(user, response_type)
    if isinstance(user, dict):
        assert "name" in user and "job" in user
    else:
        assert user.name and user.job


@pytest.mark.parametrize(
    "client",
    [
        sync_dataclass_client,
        sync_pydantic_client,
        sync_dictionary_client,
    ],
)
def test_sync_delete_user(client):
    response = client.delete_user(1)
    assert isinstance(response, httpx.Response)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "client",
    [
        sync_dataclass_client,
        sync_pydantic_client,
        sync_dictionary_client,
    ],
)
def test_sync_delete_user_type_hinted_method(client):
    response = client.delete_user_explicit_typehint(1)
    assert isinstance(response, httpx.Response)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "client,item_type",
    [
        (sync_dataclass_client, dataclass.Post),
        (sync_pydantic_client, pydantic.Post),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_get_posts_list(client, item_type):
    posts = client.get_posts_by_resource()
    assert isinstance(posts, list)
    assert len(posts) == 100
    assert isinstance(posts[0], item_type)


@pytest.mark.parametrize(
    "client,response_type",
    [
        (sync_dataclass_client, dataclass.Post),
        (sync_pydantic_client, pydantic.Post),
        (sync_dictionary_client, dict),
    ],
)
def test_sync_get_post(client, response_type):
    post = client.get_post(1)
    assert isinstance(post, response_type)
    if isinstance(post, dict):
        assert post.get("id") == 1
    else:
        assert post.id == 1


@pytest.mark.parametrize(
    "class_proxies,method_proxies,expected",
    [
        (
            "http://127.0.0.1:2023",
            "https://127.0.0.1:2024",
            "https://127.0.0.1:2024",
        ),
        (
            "http://127.0.0.1:2020",
            "http://127.0.0.1:2021",
            "http://127.0.0.1:2021",
        ),
        (
            "http://127.0.0.1:2021",
            "http://127.0.0.1:2022",
            "http://127.0.0.1:2022",
        ),
        (
            Proxy(url="http://127.0.0.1:2012"),
            URL(url="http://127.0.0.2:2013"),
            URL(url="http://127.0.0.2:2013"),
        ),
        (
            URL(url="http://127.0.0.2:2013"),
            None,
            URL(url="http://127.0.0.2:2013"),
        ),
        (
            "http://127.0.0.1:2022",
            Proxy(url="http://127.0.0.1:2012"),
            Proxy(url="http://127.0.0.1:2012"),
        ),
        (
            URL(url="http://127.0.0.2:2013"),
            URL(url="http://127.0.0.2:2014"),
            URL(url="http://127.0.0.2:2014"),
        ),
    ],
)
def test_proxies(
    class_proxies, method_proxies, expected, mocker: MockerFixture
):
    httpx_client_mock = mocker.patch(
        "declarativex.executors.httpx.Client",
        MagicMock(),
    )
    httpx_client_mock.return_value.__enter__.return_value = Mock(
        send=Mock(
            return_value=Response(
                200,
                json={"dummy": "data"},
                request=Mock(
                    wraps=httpx.Request("GET", "https://jsonplaceholder.typicode.com/users")
                ),
            )
        )
    )

    class DummyClient(BaseClient):
        proxies = class_proxies

        @http("GET", "users", proxies=method_proxies)
        def get_users(self) -> dict:
            ...

    client = DummyClient(base_url="https://jsonplaceholder.typicode.com")
    client.get_users()
    actual = httpx_client_mock.call_args_list[0][1]["proxy"]
    # Use repr() because httpx.Proxy does not implement __eq__
    assert repr(actual) == repr(expected)


def test_files_field(mocker: MockerFixture):
    httpx_client_mock = mocker.patch(
        "declarativex.executors.httpx.Client",
        MagicMock(),
    )
    send_mock = httpx_client_mock.return_value.__enter__.return_value = Mock(
        send=Mock(
            return_value=Response(
                200,
                json={"dummy": "data"},
                request=Mock(
                    wraps=httpx.Request("GET", "https://jsonplaceholder.typicode.com/users")
                ),
            )
        )
    )

    @http("POST", "users", base_url="https://jsonplaceholder.typicode.com")
    def get_users(files: Annotated[dict, Files]) -> dict:
        ...

    file = open("tests/fixtures/__init__.py", "rb")
    file_content = file.read()
    file.seek(0)
    get_users(files={"file": file})
    assert (
        "multipart/form-data"
        in send_mock.send.call_args_list[0].args[0].headers["content-type"]
    )
    assert file_content in send_mock.send.call_args_list[0].args[0].read()


def test_multiple_instances():
    PMAN_URL = "https://postman-echo.com"
    INVALID_URL = "https://invalid.com"

    class EchoClient(BaseClient):
        @http("get", "/get")
        def sample_get(self) -> dict:
            ...

    auth1 = httpx.BasicAuth("client1", "secret1")
    client1 = EchoClient(
        base_url=PMAN_URL,
        default_headers={"x-request-origin": "client1"},
        default_query_params={"x-my-param": "client1-param"},
        auth=auth1,
    )

    result1 = client1.sample_get()
    assert result1["headers"]["x-request-origin"] == "client1"
    assert result1["args"]["x-my-param"] == "client1-param"

    auth2 = httpx.BasicAuth("client2", "secret2")
    client2 = EchoClient(
        base_url=INVALID_URL,
        default_headers={"x-request-origin": "client2"},
        default_query_params={"x-my-param": "client2-param"},
        auth=auth2,
    )

    with pytest.raises(httpx.RequestError):
        client2.sample_get()
