from math import atan2, cos, radians, sin, sqrt


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    return 2 * earth_radius_km * atan2(sqrt(a), sqrt(1 - a))


def estimate_drive_minutes(distance_km: float, average_speed_kmh: float = 75.0) -> int:
    return round((distance_km / average_speed_kmh) * 60)
