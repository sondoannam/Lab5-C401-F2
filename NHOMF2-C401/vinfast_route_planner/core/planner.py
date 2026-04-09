from core.config import VEHICLE
from core.models import RouteStop, Station
from data.station_repository import load_stations
from services.distance_service import estimate_drive_minutes, haversine_km


DESTINATION_COORDS = {
    "Da Nang": (16.0544, 108.2022),
}


ORIGIN_COORDS = {
    "Ha Noi": (21.0285, 105.8542),
}


def _soc_after_drive(soc_in: float, distance_km: float) -> float:
    energy_used = VEHICLE["e_kwh_per_km"] * distance_km
    return soc_in - (energy_used / VEHICLE["Q_kwh"])


def _charge_minutes(soc_arrive: float, soc_depart: float, station_kw: float) -> int:
    p_effective = min(VEHICLE["p_vehicle_kw"], station_kw)
    energy_to_add = (soc_depart - soc_arrive) * VEHICLE["Q_kwh"]
    return round((energy_to_add / p_effective) * 60)


def _sorted_candidate_stations(origin: tuple[float, float], destination: tuple[float, float]) -> list[Station]:
    destination_lat, destination_lon = destination
    stations = load_stations()
    filtered = [
        station
        for station in stations
        if haversine_km(origin[0], origin[1], station.lat, station.lon)
        < haversine_km(origin[0], origin[1], destination_lat, destination_lon)
    ]
    return sorted(filtered, key=lambda station: station.lat, reverse=True)


def plan_route(origin: str, destination: str, soc_current: float, soc_comfort: float = 0.20) -> dict:
    origin_coords = ORIGIN_COORDS.get(origin)
    destination_coords = DESTINATION_COORDS.get(destination)
    if origin_coords is None or destination_coords is None:
        return {
            "stops": [],
            "total_time_min": 0,
            "feasible": False,
            "warnings": ["Origin/destination chua duoc mock trong MVP."],
            "soc_hard": VEHICLE["soc_hard"],
            "soc_comfort": soc_comfort,
        }

    current_soc = soc_current
    current_coords = origin_coords
    total_time = 0
    warnings: list[str] = []
    stops: list[RouteStop] = []
    candidates = _sorted_candidate_stations(origin_coords, destination_coords)

    while True:
        distance_to_destination = haversine_km(
            current_coords[0],
            current_coords[1],
            destination_coords[0],
            destination_coords[1],
        )
        soc_at_destination = _soc_after_drive(current_soc, distance_to_destination)
        if soc_at_destination >= VEHICLE["soc_hard"]:
            total_time += estimate_drive_minutes(distance_to_destination)
            if soc_at_destination < soc_comfort:
                warnings.append("Buffer mong o chang cuoi, can nhac sac som hon.")
            break

        reachable = []
        for station in candidates:
            if any(stop.station.id == station.id for stop in stops):
                continue
            distance_km = haversine_km(
                current_coords[0], current_coords[1], station.lat, station.lon
            )
            soc_arrive = _soc_after_drive(current_soc, distance_km)
            if soc_arrive >= VEHICLE["soc_hard"]:
                reachable.append((station, distance_km, soc_arrive))

        if not reachable:
            return {
                "stops": [stop.to_dict() for stop in stops],
                "total_time_min": total_time,
                "feasible": False,
                "warnings": ["Khong co tram sac kha dung tiep theo voi muc pin hien tai."],
                "soc_hard": VEHICLE["soc_hard"],
                "soc_comfort": soc_comfort,
            }

        station, distance_km, soc_arrive = max(
            reachable,
            key=lambda item: haversine_km(
                item[0].lat, item[0].lon, destination_coords[0], destination_coords[1]
            ) * -1,
        )
        soc_depart = max(VEHICLE["soc_target_default"], soc_comfort)
        charge_min = _charge_minutes(soc_arrive, soc_depart, station.p_station_kw)
        drive_min = estimate_drive_minutes(distance_km)

        if soc_arrive < soc_comfort:
            warnings.append(
                f"Buffer mong khi den {station.name}: {round(soc_arrive * 100)}%."
            )

        stops.append(
            RouteStop(
                station=station,
                distance_from_prev_km=round(distance_km, 1),
                drive_min_from_prev=drive_min,
                soc_arrive=round(soc_arrive, 3),
                soc_depart=round(soc_depart, 3),
                charge_min=charge_min,
            )
        )
        total_time += drive_min + charge_min
        current_coords = (station.lat, station.lon)
        current_soc = soc_depart

    return {
        "stops": [stop.to_dict() for stop in stops],
        "total_time_min": total_time,
        "feasible": True,
        "warnings": warnings,
        "soc_hard": VEHICLE["soc_hard"],
        "soc_comfort": soc_comfort,
    }
