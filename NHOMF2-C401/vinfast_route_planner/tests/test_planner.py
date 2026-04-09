from core.planner import plan_route


def test_plan_route_returns_contract():
    result = plan_route("Ha Noi", "Da Nang", 0.85, 0.20)
    assert "stops" in result
    assert "total_time_min" in result
    assert "feasible" in result
    assert "warnings" in result
    assert "soc_hard" in result
    assert "soc_comfort" in result
