from enum import Enum
from typing import Any, Generator

import pytest
from flask import Flask


@pytest.fixture()
def app() -> Flask:
    """ "Fixture that creates app for testing"""
    from dhos_audit_api.app import create_app

    return create_app(testing=True, use_pgsql=True, use_sqlite=False)


@pytest.fixture
def app_context(app: Flask) -> Generator[None, None, None]:
    with app.app_context():
        yield


@pytest.fixture()
def mock_bearer_validation(mocker: Any) -> Any:
    from jose import jwt

    mocked = mocker.patch.object(jwt, "get_unverified_claims")
    mocked.return_value = {
        "sub": "1234567890",
        "name": "John Doe",
        "iat": 1_516_239_022,
        "iss": "http://localhost/",
    }
    return mocked


class CommonValues(str, Enum):
    """
    An Enum containing common values used across multiple tests.
    Also inherits from `str` to make itself serializable (and thus can be used as pytest fixture).
    """

    UUID_1 = "11111111-1111-1111-1111-111111111111"
    UUID_2 = "22222222-2222-2222-2222-222222222222"
    UUID_3 = "33333333-3333-3333-3333-333333333333"
    SOMEONE_AWESOME = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    SOMEONE_EQUALLY_AWESOME = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    SOMEONE_ELSE = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    LOGIN_SUCCESS = "Login Success"
    LOGIN_SUCCESS_DESCRIPTION = "Login was successful."
    LOGIN_FAILURE = "Login Failure"
    LOGIN_FAILURE_DESCRIPTION = "Login resulted in failure."
