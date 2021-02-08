from librusapi.token import Token
import pytest
from base64 import b64encode


def test_serialization(token):
    ts = str(token)
    t = Token(ts)
    assert t.librus_token == token.librus_token
    assert t.csrf_token == token.csrf_token


def test_invalid_base64():
    with pytest.raises((UnicodeDecodeError, ValueError)):
        t = Token("`")


def test_unpack_too_many():
    with pytest.raises(ValueError):
        t = Token(b64encode("a:b:c".encode()).decode("utf-8"))


def test_unpack_too_little():
    with pytest.raises(ValueError):
        t = Token(b64encode("a".encode()).decode("utf-8"))


def test_unpack_empty():
    with pytest.raises(ValueError):
        t = Token(b64encode("a".encode()).decode("utf-8"))
