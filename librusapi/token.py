from urllib.parse import urljoin
from requests import Session
from json import JSONDecodeError
from requests.models import Response

from requests.sessions import PreparedRequest
from librusapi.exceptions import AuthorizationError
import typing
from typing import Dict
from librusapi.urls import HEADERS
from librusapi.urls import API_URLS, INDEX_URL
from base64 import b64decode, b64encode
from requests import Request
import re


class Token:
    """Combines all necessary functions to create
    authenticated requests.

    Can be retrieved using `get_token` function.
    Or loaded from a base64 encoded string.

    Attributes:
        librus_token: DZIENNIKSID cookie
        csrf_token: CSRF token, can be used for unlimited
            amount of requests within a single session
    """

    def __init__(self, token: str = None):
        """Load both Librus token and CSRF token from
        base64 encoded string.

        e.g. base64($librus_token + ':' + $csrf_token)

        Args:
            token: base64 encoded token. 
                When is None sets all properties to an
                empty string.
        Raises:
            ValueError: Whenever there are too many or too little
                strings separated by a colon
            binascii.Error: Whenever parsing base64 encoded string fails
            UnicodeDecodeError: Whenever parsing token string from
                binary to utf-8 fails
        Example:
        >>> token = Token('THh4LXh4eHh4eHh4eHh4eHh4eHh4eHh\
            4eHh4eHh4eHh4eHh4OkNTUkZUT0tFTjEyMzQ1Njc4OQ==')
        >>> print(token.librus_token)
        Lxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        >>> print(token.csrf_token)
        CSRFTOKEN123456789
        """
        self._session = Session()
        if not token:
            self.librus_token = ""
            self.csrf_token = ""
            return
        token = b64decode(token).decode("utf-8")
        librus_token, csrf_token = token.split(":")

        self.librus_token = librus_token
        """DZIENNIKSID cookie"""
        self.csrf_token = csrf_token
        """CSRF token, can be used for unlimited 
        amount of requests within a single session"""

    def __str__(self) -> str:
        combine = self.librus_token + ":" + self.csrf_token
        return b64encode(combine.encode()).decode("utf-8")

    def create_request(
        self, method: str, url: str, data=None, files=None
    ) -> PreparedRequest:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0"
        }
        cookies = {"DZIENNIKSID": self.librus_token}
        if files:
            files["requestkey"] = (None, self.csrf_token)
        return Request(
            method, url, headers=headers, data=data, files=files, cookies=cookies
        ).prepare()

    def post_request(self, url: str, data=None, files=None) -> PreparedRequest:
        return self.create_request("POST", url, data, files)

    def get_request(self, url: str) -> PreparedRequest:
        return self.create_request("GET", url)

    def post(self, url: str, data=None, files=None) -> Response:
        req = self.post_request(url, data, files)
        resp = self._session.send(req)
        resp.raise_for_status()
        return resp

    def get(self, url: str) -> Response:
        req = self.get_request(url)
        resp = self._session.send(req)
        resp.raise_for_status()
        return resp


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
    returns instance of Token()
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

    if (goTo := json.get("goTo")) :
        s.get(urljoin(typing.cast(str, API_URLS["base_api"]), goTo))
        resp = s.get(INDEX_URL)
    else:
        raise AuthorizationError("'goTo' was not provided in the response JSON")

    cookies = s.cookies.get_dict()
    try:
        librus_token = cookies["DZIENNIKSID"]
    except KeyError:
        raise AuthorizationError(f"This should not happen. Cookies: {cookies}")
    token = Token()
    token.librus_token = librus_token
    token.csrf_token = ""
    matches = re.search(r'(?<=csrfTokenValue = ").*(?=")', resp.text)
    if not matches:
        raise AuthorizationError("CSRF token not found on Librus index page")
    token.csrf_token = matches.group(0)
    return token
