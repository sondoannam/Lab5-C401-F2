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
    assert isinstance(result["stops"], list)
    assert result["feasible"] is True


def test_plan_route_skips_unusable_stations():
    result = plan_route("Ha Noi", "Da Nang", 0.85, 0.20)
    stop_ids = [stop["station"]["id"] for stop in result["stops"]]
    assert "ST_NB_03" not in stop_ids
    assert "ST_TH_04" not in stop_ids
    assert "ST_VL_10" not in stop_ids
    assert "ST_PL_13" not in stop_ids


def test_plan_route_prefers_faster_active_route():
    result = plan_route("Ha Noi", "Da Nang", 0.85, 0.20)
    stop_ids = [stop["station"]["id"] for stop in result["stops"]]
    assert stop_ids == ["ST_VI_05", "ST_DH_09"]
    assert result["total_time_min"] == 578


def test_plan_route_low_soc_can_be_infeasible():
    result = plan_route("Ha Noi", "Da Nang", 0.12, 0.20)
    assert result["feasible"] is False
    assert result["stops"] == []
    assert "Khong co tram sac kha dung tiep theo voi muc pin hien tai." in result["warnings"]
