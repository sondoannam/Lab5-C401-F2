from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
STATIONS_FILE = BASE_DIR / "data" / "stations.json"

VEHICLE = {
    "model": "VinFast VF8",
    "Q_kwh": 82.0,
    "e_kwh_per_km": 0.22,
    "p_vehicle_kw": 150.0,
    "soc_hard": 0.10,
    "soc_comfort_default": 0.20,
    "soc_target_default": 0.80,
}

DEFAULT_ORIGIN = "Ha Noi"
DEFAULT_DESTINATION = "Da Nang"
