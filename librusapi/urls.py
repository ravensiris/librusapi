from urllib.parse import urljoin
from requests.structures import CaseInsensitiveDict

BASE_URL = "https://synergia.librus.pl/"
TIMETABLE_URL = urljoin(BASE_URL, "przegladaj_plan_lekcji")
HEADERS = CaseInsensitiveDict(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0"
    }
)

API_URLS = {
    "base_api": (baseapi := "https://api.librus.pl/"),
    "auth": {
        "_client_id": (client_id := "client_id=46"),
        "_response_type": (response_type := "response_type=code"),
        "_scope": (scope := "scope=mydata"),
        "base": (baseauth := urljoin(baseapi, "OAuth/*")),
        "handshake": urljoin(
            baseauth,
            "Authorization?" + "&".join([client_id, response_type, scope]),
        ),
        "authorization": urljoin(baseauth, "Authorization?" + client_id),
        "grant": urljoin(baseauth, "Authorization/Grant?" + client_id),
    },
}
