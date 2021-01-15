from librusapi.urls import TIMETABLE_URL, HEADERS
from librusapi.exceptions import AuthorizationError
from requests import Session
from bs4 import BeautifulSoup as bs  # type: ignore
from bs4.element import Tag  # type: ignore
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import total_ordering, cached_property
from typing import Tuple, Optional, Iterator, Union


class Week:
    """Container for a week"""

    def __init__(self, start: datetime):
        if start.weekday() != 0:
            start = start - timedelta(days=start.weekday())
        self.start = start

    @cached_property
    def end(self) -> datetime:
        return self.start + timedelta(days=6)

    @cached_property
    def ___str__(self):
        fmt = "%Y-%m-%d"
        return self.start.strftime(fmt) + "_" + self.end.strftime(fmt)

    def __str__(self):
        return self.___str__


@total_ordering
@dataclass
class LessonUnit:
    """Single lesson on a timetable"""

    name: str
    teacher: str
    classroom: str
    info: Optional[str]
    start: datetime
    duration: timedelta

    def __lt__(self, other):
        """Compares dates"""
        if not isinstance(other, LessonUnit):
            return NotImplemented
        return self.start < other.start

    def __eq__(self, other):
        if not isinstance(other, LessonUnit):
            return NotImplemented
        return self.start == other.start

    @cached_property
    def week(self):
        return Week(self.start)


def _get_html(token: str, week: Week) -> str:
    s = Session()
    data = {"tydzien": str(week)}
    cookies = {"DZIENNIKSID": token}
    r = s.post(TIMETABLE_URL, data=data, cookies=cookies, headers=HEADERS)
    r.raise_for_status()
    print(r.text)
    return r.text


def _process_entry_text(et: Tag) -> Tuple[str, str, str]:
    """Process the 'text' part of a lesson unit html"""

    def _sanitize(text):
        """Remove all newlines and >1 spaces in a line of text"""
        return " ".join(text.replace("\xa0", " ").replace("&nbsp", "").split())

    text_data = et.find_all(text=True)
    # remove unnecessary newlines found
    if len(text_data) == 4:
        del text_data[0]
        del text_data[1]
    class_name, teacher_and_classroom = text_data
    teacher_and_classroom = _sanitize(teacher_and_classroom)
    teacher, classroom = teacher_and_classroom.split(" s. ")
    teacher = _sanitize(teacher[1:])
    class_name = _sanitize(class_name)
    return class_name, classroom, teacher


def _process_entry_time(e: Tag) -> Tuple[datetime, timedelta, Optional[str]]:
    def _parse_time(time: str):
        """Parse a HH:MM string to datetime"""
        return datetime.strptime(time, "%H:%M")

    day = e.attrs.get("data-date")
    time_from = _parse_time(e.attrs.get("data-time_from"))
    time_to = _parse_time(e.attrs.get("data-time_to"))
    info = e.find("div", attrs={"class": "plan-lekcji-info"})
    if info:
        info = info.text
    start = datetime.strptime(day, "%Y-%m-%d") + timedelta(
        hours=time_from.hour, minutes=time_from.minute
    )
    duration = time_to - time_from
    return start, duration, info


def _process_entry(e: Tag, et: Tag) -> LessonUnit:
    start, duration, info = _process_entry_time(e)
    class_name, classroom, teacher = _process_entry_text(et)
    return LessonUnit(
        name=class_name,
        teacher=teacher,
        classroom=classroom,
        start=start,
        duration=duration,
        info=info,
    )


def _parse_html(html: str) -> Iterator[LessonUnit]:
    doc = bs(html, "lxml")
    no_access = doc.find("h2")
    if no_access and no_access.text == "Brak dostępu":
        raise AuthorizationError("Token invalid or expired.")
    entries = doc.find_all("td", {"id": "timetableEntryBox"})
    for e in entries:
        et = e.find("div", attrs={"class": "text"})
        if not et:
            continue
        yield _process_entry(e, et)


def lesson_units(
    token: str, week: Optional[Union[datetime, Week]] = datetime.now()
) -> Iterator[LessonUnit]:
    """List all lesson units in no particular order"""
    if isinstance(week, datetime):
        week = Week(week)
    elif not isinstance(week, Week):
        raise TypeError(
            f"week of type: {type(week)} is not allowed. Can be either datetime or core.Week"
        )
    html = _get_html(token, week)
    return _parse_html(html)
