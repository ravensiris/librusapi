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
    """Container for a week.

    Use it with str() to get the YYYY-MM-DD_YYYY-MM-DD representation
    used in librus timetable requests.

    Attributes:
        start: Any day in a week. Will be automatically changed to a Monday.
        end: End of the week.
    """

    def __init__(self, start: datetime):
        if start.weekday() != 0:
            start = start - timedelta(days=start.weekday())
        self.start = start
        """Start of the week."""

    @cached_property
    def end(self) -> datetime:
        """End of the week."""
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
    """Stores a single unit on a timetable.

    You can use comparisons to determine which lesson starts first.

    Attributes:
        name: Lesson's name.
        teacher: Teacher's full name.
        classroom: Class' room string.
        info: Additional info attached to a unit.
            Can be for example: 'dzien wolny od szkoly', 'zastepstwo'
        start: Full `datetime` of lesson's start time
        duration: Duration in `timedelta`
        week: `Week` of the lesson

    """

    name: str
    """Lesson's name"""
    teacher: str
    """Teacher's full name."""
    classroom: str
    """ Class' room."""
    info: Optional[str]
    """Additional info attached to a unit. """
    start: datetime
    """Full `datetime` of lesson's start time"""
    duration: timedelta
    """Lesson's duration"""

    def __lt__(self, other):
        """Compares dates of units"""
        if not isinstance(other, LessonUnit):
            return NotImplemented
        return self.start < other.start

    def __eq__(self, other):
        """Compares dates of units"""
        if not isinstance(other, LessonUnit):
            return NotImplemented
        return self.start == other.start

    @cached_property
    def week(self):
        """`Week` of the lesson"""
        return Week(self.start)


def _get_html(token: str, week: Week) -> str:
    s = Session()
    data = {"tydzien": str(week)}
    cookies = {"DZIENNIKSID": token}
    r = s.post(TIMETABLE_URL, data=data, cookies=cookies, headers=HEADERS)
    r.raise_for_status()
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
    """Generator for lesson units.

    Retrieves HTML and then parses it using Beautifulsoup.

    Args:
        token: Librus token.
            Can be retrieved from `librusapi.token.get_token`.
        week: Determines which week will be fetched from librus
            Either a `Week` or any day which will be converted to `Week`.
            Defaults to `datetime.now()`
    Returns:
        Generator of `LessonUnit` that parses one instance at a time.
        Results are unordered.
    Raises:
        requests.exceptions.HTTPError: When an error that is
            unrelated to authenticaiton occurs.
        AuthorizationError: When authorization using the token fails.
    Example:
    >>> lesson_units = lesson_units('TOKEN')
    >>> for lu in lesson_units:
    ...     print(lu.name, lu.teacher, lu.classroom, lu.info, lu.start, lu.duration, sep='\\n')
    ...     break
    Math
    John Smith
    111
    None
    2021-01-11 08:00:00
    0:45:00
    """
    if not week:
        week = datetime.now()

    if isinstance(week, datetime):
        week = Week(week)
    html = _get_html(token, week)
    return _parse_html(html)
