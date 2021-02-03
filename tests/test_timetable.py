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

def test_all_weeks(token):
    now = datetime.now()
    year = now.year if now.month >= 9 else now.year - 1
    start = datetime(year, 9, 1)
    while start < now:
        for unit in timetable.lesson_units(token, start):
            assert unit.name
            assert unit.start
            assert unit.teacher
            assert unit.duration
        start = start + timedelta(days=7)
