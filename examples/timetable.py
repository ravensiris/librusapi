#!/usr/bin/env python3

from librusapi.token import get_token
from librusapi import timetable

creds = load(open("../tests.json", "r"))
token = get_token(creds["username"], creds["password"])
lesson_units = timetable.lesson_units(token)

for lu in lesson_units:
    print(lu)
