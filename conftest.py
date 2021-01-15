"""Tests require a 'tests.json' file with username and password
Example: {"username":"123456u", "password": "password123"}"""

import pytest
from core.token import get_token
from json import load

pytest_plugins = ("mypy", "flake8")


@pytest.fixture(scope="session")
def token():
    with open("tests.json", "r", encoding="utf-8") as f:
        creds = load(f)
        username, password = creds.get("username"), creds.get("password")
    return get_token(username, password)
