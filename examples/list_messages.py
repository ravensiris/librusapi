#!/usr/bin/env python3

from librusapi.token import get_token
from librusapi import messages
from json import load

creds = load(open("../tests.json", "r"))
token = get_token(creds["username"], creds["password"])
page_info, messages = messages.list_messages(token, 0)

for msg in messages:
    print(msg)
