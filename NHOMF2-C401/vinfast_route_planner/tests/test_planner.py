from data.station_repository import load_metadata, load_stations
from core.planner import plan_route


def test_mock_station_dataset_loads():
    metadata = load_metadata()
    stations = load_stations()
    assert metadata["vehicle_config"]["model"] == "VinFast VF8"
    assert len(stations) == 15
    assert stations[0].status == "active"


def test_plan_route_returns_contract():
    result = plan_route("Ha Noi", "Da Nang", 0.85, 0.20)
    assert "stops" in result
    assert "total_time_min" in result
    assert "feasible" in result
    assert "warnings" in result
    assert "soc_hard" in result
    assert "soc_comfort" in result
