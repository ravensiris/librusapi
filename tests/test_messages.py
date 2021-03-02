from librusapi import messages
import pytest


@pytest.fixture(scope="module")
def max_page(token):
    msg_page = messages.get_page(token, 0)
    return msg_page.total_pages - 1


@pytest.mark.parametrize("page", range(10))
def test_messages_page(token, page, max_page):
    if page > max_page:
        return
    msg_page = messages.get_page(token, page)
    assert msg_page.page == page
    for msg in msg_page.messages:
        assert isinstance(msg, messages.MessageBrief)
