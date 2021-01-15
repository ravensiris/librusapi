from librusapi import timetable
from datetime import datetime, timedelta


def test_week():
    d = datetime.strptime("2020-08-31", "%Y-%m-%d")
    w = timetable.Week(d)
    assert w.start == d
    assert w.end == d + timedelta(days=6)
    assert str(w) == "2020-08-31_2020-09-06"


def test_lesson_units(token):
    r = timetable.lesson_units(token)
    r = list(r)
    assert len(r) > 0