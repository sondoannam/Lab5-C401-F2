from functools import lru_cache

import requests

OSRM_BASE_URL = "http://router.project-osrm.org"


@lru_cache(maxsize=512)
def _cached_route_info(
    base_url: str,
    timeout: int,
    p1_lat: float,
    p1_lon: float,
    p2_lat: float,
    p2_lon: float,
):
    coord1 = f"{p1_lon},{p1_lat}"
    coord2 = f"{p2_lon},{p2_lat}"
    url = f"{base_url}/route/v1/driving/{coord1};{coord2}?overview=full&geometries=geojson"

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        return None

    route = data["routes"][0]
    return {
        "distance_km": round(route["distance"] / 1000, 2),
        "duration_min": round(route["duration"] / 60, 2),
        "geometry": route["geometry"],
    }


class OSRMClient:
    def __init__(self, base_url=OSRM_BASE_URL, timeout=2):
        self.base_url = base_url
        self.timeout = timeout

    def get_route_info(self, p1, p2):
        """
        p1, p2: tuple (lat, lon)
        return: dict {distance_km, duration_min, geometry} | None
        """

        try:
            return _cached_route_info(
                self.base_url,
                self.timeout,
                p1[0],
                p1[1],
                p2[0],
                p2[1],
            )

        except requests.exceptions.Timeout:
            print("⏰ OSRM request timeout")
            return None

        except requests.exceptions.RequestException as e:
            print("❌ OSRM request error:", e)
            return None

        except Exception as e:
            print("⚠️ Unexpected error:", e)
            return None


# ===== TEST =====
if __name__ == "__main__":
    client = OSRMClient()

    p1 = (21.0285, 105.8542)
    p2 = (16.0544, 108.2022)

    result = client.get_route_info(p1, p2)

    if result:
        print("Distance (km):", result["distance_km"])
        print("Duration (min):", result["duration_min"])
        print("Has geometry:", "geometry" in result)
    else:
        print("❌ Failed to get route")
