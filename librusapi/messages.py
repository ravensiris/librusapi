from dataclasses import dataclass
from datetime import datetime
from librusapi.token import Token
from typing import Iterator, Optional, Tuple

from requests.sessions import Session, Request
from librusapi.urls import MESSAGES_URL
from librusapi.helpers import sanitize

from bs4 import BeautifulSoup

import re


@dataclass
class MessageBrief:
    """A quick briefing of a message.

    Has necessary information to retrieve the full message.

    Attributes:
        id: message id
        title: message title
        sender: sender alias and full name between brackets
            e.g. admin (John Doe)
        sent: when was the message sent
        has_attachment: whether message contains an attachment
        is_read: whether message was read or not
    """

    id: str
    title: str
    sender: str
    sent: datetime
    has_attachment: bool
    is_read: bool


def _message_list_get_html(token: Token, page: int) -> str:
    payload = {
        "filtrUzytkownikow": 0,
        "idPojemnika": 105,
        "opcja_zaznaczone_g": 0,
        "filtr_uzytkownikow": "-",
        "sortujTabele[tabeleKolumna]": 3,
        "sortujTabele[tabeleKierunek]": 1,
        "sortujTabele[tabelePojemnik]": 105,
        "sortowanie[105][0]": "",
        "sortowanie[105][1]": "",
        "sortowanie[105][2]": "",
        "opcja_zaznaczone_d": 0,
        "numer_strony105": page,
        "porcjowanie_pojemnik105": 105,
        "poprzednia": 5,
    }
    # Don't send file="$NAME" field
    for k, v in payload.items():
        payload[k] = (None, v)

    resp = token.post(MESSAGES_URL, files=payload)
    return resp.text


@dataclass
class PageInfo:
    """Stores page related information for paginated requests"""
    current: int
    max_page: int


def _parse_message_page_info(doc: BeautifulSoup) -> PageInfo:
    elem = doc.find("div", class_="pagination").find("span")
    pagination_desc = sanitize(elem.text)
    match = re.findall("[0-9][^ ]*", pagination_desc)
    current = int(match[0]) - 1
    max_page = int(match[1]) - 1
    return PageInfo(current, max_page)


def _parse_message_briefs(doc: BeautifulSoup) -> Iterator[MessageBrief]:
    table = doc.find("table", class_="decorated stretch").find("tbody")
    trs = table.find_all("tr")
    for tr in trs:
        links = tr.find_all("a")
        inp = tr.find("input")
        id = inp.attrs.get("value")
        sender_elem = links[0]
        is_read = "style" not in sender_elem.parent.attrs
        has_attachment = tr.find("img") is not None
        sender = sanitize(sender_elem.text)
        title = sanitize(links[1].text)
        date_str = sanitize(tr.find("td", class_="medium center").text)
        sent = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        yield MessageBrief(id, title, sender, sent, has_attachment, is_read)


def list_messages(token: Token, page: int) -> Tuple[PageInfo, Iterator[MessageBrief]]:
    """Generator for `MessageBrief`

    Retrieves HTML and then parses it using Beautifulsoup.

    Args:
        token: Librus token.
            Can be retrieved from `librusapi.token.get_token`.
        page: Which page to retrieve
    Returns:
        `PageInfo` and Generator of `MessageBrief`
    Raises:
        requests.exceptions.HTTPError: When an error that is
            unrelated to authenticaiton occurs.
        AuthorizationError: When authorization using the token fails.
        IndexError: When page is out of bounds
    Example:
    >>> messages = list_messages(token)
    >>> for msg in messages:
    ...     print(msg.id, msg.title, msg.sender, msg.sent, msg.has_attachment, msg.is_read  sep='\\n')
    ...     break
    12345678
    Welcome to the school system!
    John Smith
    2021-01-11 08:00:00
    False
    False
    """
    html = _message_list_get_html(token, page)
    doc = BeautifulSoup(html, features="lxml")
    info = _parse_message_page_info(doc)
    if info.current != page:
        raise IndexError(f"Page doesn't exist! Max page: {info.max_page}")
    msgs = _parse_message_briefs(doc)
    return info, msgs
