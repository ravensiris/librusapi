from librusapi.token import Token
from librusapi.urls import INDEX_URL
import pytest
from base64 import b64encode


def test_startpage(token: Token):
    resp = token.get(INDEX_URL)
    resp.raise_for_status()

