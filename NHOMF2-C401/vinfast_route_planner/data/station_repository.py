import json

from core.config import STATIONS_FILE
from core.models import Station


def load_stations() -> list[Station]:
    with open(STATIONS_FILE, "r", encoding="utf-8") as file:
        raw_stations = json.load(file)
    return [Station(**station) for station in raw_stations]
