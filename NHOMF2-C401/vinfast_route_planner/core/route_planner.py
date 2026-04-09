

from functools import lru_cache

from vinfast_route_planner.services.osrm_client import OSRMClient
from vinfast_route_planner.core.config import VEHICLE
from vinfast_route_planner.core.models import RouteStop, Station
from vinfast_route_planner.services.distance_service import (
    estimate_drive_minutes,
    haversine_km,
)
from vinfast_route_planner.utils.data_loader import (
    filter_active_stations,
    get_station_by_name,
    load_metadata,
    load_stations,
)


DATASET_METADATA = load_metadata()
VEHICLE_CONFIG = DATASET_METADATA.get("vehicle_config", {})
SAFETY_CONSTRAINTS = DATASET_METADATA.get("safety_constraints", {})

PLANNER_VEHICLE = {
    "model": VEHICLE_CONFIG.get("model", VEHICLE["model"]),
    "Q_kwh": float(VEHICLE_CONFIG.get("battery_capacity_kwh", VEHICLE["Q_kwh"])),
    "e_kwh_per_km": float(
        VEHICLE_CONFIG.get("avg_consumption_kwh_per_km", VEHICLE["e_kwh_per_km"])
    ),
    "p_vehicle_kw": float(
        VEHICLE_CONFIG.get("max_charge_power_vehicle_kw", VEHICLE["p_vehicle_kw"])
    ),
    "soc_hard": float(
        SAFETY_CONSTRAINTS.get("soc_hard_min_percent", VEHICLE["soc_hard"] * 100)
    )
    / 100,
    "soc_comfort_default": float(
        SAFETY_CONSTRAINTS.get(
            "soc_comfort_min_percent", VEHICLE["soc_comfort_default"] * 100
        )
    )
    / 100,
    "soc_target_default": VEHICLE["soc_target_default"],
    "default_setup_time_min": int(VEHICLE_CONFIG.get("default_setup_time_min", 0)),
}

DESTINATION_COORDS = {
    "Da Nang": (16.0544, 108.2022),
    "Danang": (16.0544, 108.2022),
}


ORIGIN_COORDS = {
    "Ha Noi": (21.0285, 105.8542),
    "Hanoi": (21.0285, 105.8542),
}


def _resolve_location(
    name: str, fallback_coords: dict[str, tuple[float, float]]
) -> tuple[float, float] | None:
    if name in fallback_coords:
        return fallback_coords[name]
    station = get_station_by_name(name)
    if station is None:
        return None
    return (station.lat, station.lon)


def _distance_to_destination(
    coords: tuple[float, float], destination: tuple[float, float]
) -> float:
    return haversine_km(coords[0], coords[1], destination[0], destination[1])


def _soc_after_drive(soc_in: float, distance_km: float) -> float:
    energy_used = PLANNER_VEHICLE["e_kwh_per_km"] * distance_km
    return soc_in - (energy_used / PLANNER_VEHICLE["Q_kwh"])


def _charge_minutes(
    soc_arrive: float,
    soc_depart: float,
    station_kw: float,
    setup_time_min: int,
) -> int:
    p_effective = min(PLANNER_VEHICLE["p_vehicle_kw"], station_kw)
    energy_to_add = (soc_depart - soc_arrive) * PLANNER_VEHICLE["Q_kwh"]
    charging_time_min = round((energy_to_add / p_effective) * 60)
    return charging_time_min + setup_time_min


def _sorted_candidate_stations(
    origin: tuple[float, float], destination: tuple[float, float]
) -> list[Station]:
    stations = load_stations()
    active_stations = filter_active_stations(stations)
    filtered = [
        station
        for station in active_stations
        if _distance_to_destination((station.lat, station.lon), destination)
        < _distance_to_destination(origin, destination)
    ]
    return sorted(
        filtered,
        key=lambda station: _distance_to_destination(
            (station.lat, station.lon), destination
        ),
        reverse=True,
    )


def _reachable_next_stations(
    current_coords: tuple[float, float],
    current_soc: float,
    destination_coords: tuple[float, float],
    candidates: list[Station],
    used_station_ids: frozenset[str],
) -> list[tuple[Station, float, float]]:
    reachable = []
    current_distance_to_destination = _distance_to_destination(
        current_coords, destination_coords
    )
    for station in candidates:
        if station.id in used_station_ids:
            continue
        station_coords = (station.lat, station.lon)
        if (
            _distance_to_destination(station_coords, destination_coords)
            >= current_distance_to_destination
        ):
            continue
        distance_km = haversine_km(
            current_coords[0], current_coords[1], station.lat, station.lon
        )
        soc_arrive = _soc_after_drive(current_soc, distance_km)
        if soc_arrive >= PLANNER_VEHICLE["soc_hard"]:
            reachable.append((station, distance_km, soc_arrive))
    return reachable


def plan_route(
    origin: str, destination: str, soc_current: float, soc_comfort: float = 0.20
) -> dict:
    origin_coords = _resolve_location(origin, ORIGIN_COORDS)
    destination_coords = _resolve_location(destination, DESTINATION_COORDS)

    if origin_coords is None or destination_coords is None:
        return {
            "stops": [],
            "total_time_min": 0,
            "feasible": False,
            "warnings": ["Origin/destination chua duoc mock trong MVP."],
            "soc_hard": PLANNER_VEHICLE["soc_hard"],
            "soc_comfort": soc_comfort,
            "geometry": None,
        }

    if origin_coords == destination_coords:
        return {
            "stops": [],
            "total_time_min": 0,
            "feasible": True,
            "warnings": [],
            "soc_hard": PLANNER_VEHICLE["soc_hard"],
            "soc_comfort": soc_comfort,
            "geometry": None,
        }

    candidates = _sorted_candidate_stations(origin_coords, destination_coords)

    @lru_cache(maxsize=None)
    def _best_plan(
        current_coords: tuple[float, float],
        current_soc_state: float,
        used_station_ids: frozenset[str],
    ):
        distance_to_destination = haversine_km(
            current_coords[0],
            current_coords[1],
            destination_coords[0],
            destination_coords[1],
        )

        soc_at_destination = _soc_after_drive(current_soc_state, distance_to_destination)

        if soc_at_destination >= PLANNER_VEHICLE["soc_hard"]:
            return (
                estimate_drive_minutes(distance_to_destination),
                [],
                soc_at_destination,
            )

        reachable = _reachable_next_stations(
            current_coords,
            current_soc_state,
            destination_coords,
            candidates,
            used_station_ids,
        )

        if not reachable:
            return None

        best_option = None
        best_total_time = None
        target_soc = max(PLANNER_VEHICLE["soc_target_default"], soc_comfort)

        for station, distance_km, soc_arrive in reachable:
            drive_min = estimate_drive_minutes(distance_km)

            charge_min = _charge_minutes(
                soc_arrive,
                target_soc,
                station.p_station_kw,
                station.setup_time_min or PLANNER_VEHICLE["default_setup_time_min"],
            )

            next_plan = _best_plan(
                (station.lat, station.lon),
                round(target_soc, 4),
                used_station_ids | frozenset({station.id}),
            )

            if next_plan is None:
                continue

            future_time, future_stops, destination_soc = next_plan
            total_time = drive_min + charge_min + future_time

            current_stop = (station, distance_km, soc_arrive, charge_min, target_soc)

            if best_total_time is None or total_time < best_total_time:
                best_total_time = total_time
                best_option = (
                    total_time,
                    [current_stop, *future_stops],
                    destination_soc,
                )

        return best_option

    best_plan = _best_plan(origin_coords, round(soc_current, 4), frozenset())

    if best_plan is None:
        return {
            "stops": [],
            "total_time_min": 0,
            "feasible": False,
            "warnings": ["Khong co tram sac kha dung tiep theo voi muc pin hien tai."],
            "soc_hard": PLANNER_VEHICLE["soc_hard"],
            "soc_comfort": soc_comfort,
            "geometry": None,
        }

    total_time, stop_specs, destination_soc = best_plan

    warnings = []
    stops = []

    for station, distance_km, soc_arrive, charge_min, soc_depart in stop_specs:
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

    if destination_soc < soc_comfort:
        warnings.append("Buffer mong o chang cuoi, can nhac sac som hon.")

    # ===== BUILD GEOMETRY (🔥 PHẦN MỚI) =====
    client = OSRMClient()

    waypoints = [origin_coords]
    for stop in stops:
        waypoints.append((stop.station.lat, stop.station.lon))
    waypoints.append(destination_coords)

    full_geometry = []

    for i in range(len(waypoints) - 1):
        segment = client.get_route_info(waypoints[i], waypoints[i + 1])

        if segment and segment.get("geometry"):
            coords = segment["geometry"]["coordinates"]

            if i > 0:
                coords = coords[1:]  # tránh trùng điểm

            full_geometry.extend(coords)

    return {
        "stops": [stop.to_dict() for stop in stops],
        "total_time_min": int(total_time),
        "feasible": True,
        "warnings": warnings,
        "soc_hard": PLANNER_VEHICLE["soc_hard"],
        "soc_comfort": soc_comfort,
        "geometry": {
            "type": "LineString",
            "coordinates": full_geometry,
        }
        if full_geometry
        else None,
    }