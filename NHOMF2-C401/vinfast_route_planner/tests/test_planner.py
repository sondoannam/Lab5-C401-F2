from vinfast_route_planner.core.route_planner import plan_route
from vinfast_route_planner.utils.data_loader import (
    list_station_names,
    load_metadata,
    load_stations,
)


def test_mock_station_dataset_loads():
    metadata = load_metadata()
    stations = load_stations()
    assert metadata["vehicle_config"]["model"] == "VinFast VF8"
    assert len(stations) == 15
    assert stations[0].status == "active"
    for s in stations:
        assert s.p_station_kw > 0
        assert -90 <= s.lat <= 90
        assert -180 <= s.lon <= 180


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


def test_station_names_available_for_ui_options():
    station_names = list_station_names()
    assert "VinFast Da Nang Center" in station_names
    assert "Siêu trạm sạc VinFast TP. Vinh" in station_names


def test_plan_route_accepts_station_name_destination():
    result = plan_route("Ha Noi", "VinFast Da Nang Center", 0.85, 0.20)
    assert result["feasible"] is True
    assert len(result["stops"]) >= 1


def test_plan_route_same_origin_destination():
    result = plan_route("Ha Noi", "Ha Noi", 0.85, 0.20)
    assert result["feasible"] is True
    assert len(result["stops"]) == 0
    assert result["total_time_min"] == 0


def test_plan_route_unknown_location():
    result = plan_route("UnknownCity", "Da Nang", 0.85, 0.20)
    assert result["feasible"] is False
    assert "Origin/destination chua duoc mock trong MVP." in result["warnings"]
