
import requests


class HHSession:
    _session: requests.Session | None = None

    @classmethod
    def get(cls) -> requests.Session:
        if cls._session is None:
            cls._session = requests.Session()
            cls._session.headers.update({
                "HH-User-Agent": "PythonHHParser/1.2 (4elobek0012@gmail.com)"
            })
        return cls._session