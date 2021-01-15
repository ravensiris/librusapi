from urllib.parse import urljoin
from requests.structures import CaseInsensitiveDict

BASE_URL = "https://synergia.librus.pl/"
TIMETABLE_URL = urljoin(BASE_URL, "przegladaj_plan_lekcji")
HEADERS = CaseInsensitiveDict({
    "User-Agent": "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0"
})