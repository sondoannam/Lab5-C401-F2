from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Station:
    id: str
    name: str
    lat: float
    lon: float
    p_station_kw: float
    type: str
    amenities: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RouteStop:
    station: Station
    distance_from_prev_km: float
    drive_min_from_prev: int
    soc_arrive: float
    soc_depart: float
    charge_min: int

    def to_dict(self) -> dict:
        return {
            "station": self.station.to_dict(),
            "distance_from_prev_km": self.distance_from_prev_km,
            "drive_min_from_prev": self.drive_min_from_prev,
            "soc_arrive": self.soc_arrive,
            "soc_depart": self.soc_depart,
            "charge_min": self.charge_min,
        }
