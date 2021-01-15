from urllib.parse import urljoin
from requests import Session
from json import JSONDecodeError
from librusapi.exceptions import AuthorizationError
import typing
from typing import Dict
from librusapi.urls import HEADERS
from librusapi.urls import API_URLS


def get_token(login: str, password: str):
    """Get DZIENNIKSID cookie that acts as an authorization token.

    Args:
        login: Full Librus username.
        password: Librus password.
    Returns:
        string DZIENNIKSID cookie.
    Raises:
        AuthorizationError: Whenever anything fails.

    Example:
    >>> get_token('username', 'password')
    Lxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
    s = Session()
    s.headers = HEADERS
    s.get(
        url=typing.cast(
            str, typing.cast(Dict[str, dict], API_URLS["auth"])["handshake"]
        )
    )
    resp = s.post(
        typing.cast(
            str, typing.cast(Dict[str, dict], API_URLS["auth"])["authorization"]
        ),
        data={"action": "login", "login": login, "pass": password},
    )

    try:
        json = resp.json()
    except JSONDecodeError:
        raise AuthorizationError("Invalid username and/or password")

    if not (status := json.get("status")) == "ok" and status == "error":
        error_messages = [e.get("message") for e in json.get("errors")]
        raise AuthorizationError("\n".join(error_messages))

    if (goTo := json.get("goTo")):
        s.get(urljoin(typing.cast(str, API_URLS["base_api"]), goTo))
    else:
        raise AuthorizationError("'goTo' was not provided in the response JSON")

    cookies = s.cookies.get_dict()

    try:
        return cookies["DZIENNIKSID"]
    except KeyError:
        raise AuthorizationError(f"This should not happen. Cookies: {cookies}")