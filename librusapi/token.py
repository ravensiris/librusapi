from urllib.parse import urljoin
from requests import Session
from json import JSONDecodeError
from librusapi.exceptions import AuthorizationError
import typing
from typing import Dict
from librusapi.urls import HEADERS

URLS = {
    "base_api": (baseapi := "https://api.librus.pl/"),
    "auth": {
        "_client_id": (client_id := "?client_id=46"),
        "base": (baseauth := urljoin(baseapi, "OAuth/*")),
        "authorization": urljoin(baseauth, "Authorization" + client_id),
        "grant": urljoin(baseauth, "Authorization/Grant" + client_id),
    },
}


def get_token(login: str, _pass: str):
    """Get DZIENNIKSID cookie that acts as an authorization token"""
    s = Session()
    s.headers = HEADERS
    s.get(
        url="https://api.librus.pl/OAuth/Authorization?\
                client_id=46&response_type=code&scope=mydata"
    )
    resp = s.post(
        typing.cast(str, typing.cast(Dict[str, dict], URLS["auth"])["authorization"]),
        data={"action": "login", "login": login, "pass": _pass},
    )

    try:
        json = resp.json()
    except JSONDecodeError:
        raise AuthorizationError("Invalid username and/or password")

    if not (status := json.get("status")) == "ok" and status == "error":
        error_messages = [e.get("message") for e in json.get("errors")]
        raise AuthorizationError("\n".join(error_messages))

    if (goTo := json.get("goTo")):
        s.get(urljoin(typing.cast(str, URLS["base_api"]), goTo))
    else:
        raise AuthorizationError("'goTo' was not provided in the response JSON")

    cookies = s.cookies.get_dict()

    try:
        return cookies["DZIENNIKSID"]
    except KeyError:
        raise AuthorizationError(f"This should not happen. Cookies: {cookies}")