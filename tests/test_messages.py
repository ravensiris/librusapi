from librusapi.messages import list_messages
import pytest

def test_message_list(token):
    list(list_messages(token, 0))

def test_nonexistent_page(token):
    with pytest.raises(IndexError):
        list(list_messages(token, 999))