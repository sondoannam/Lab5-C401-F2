from vinfast_route_planner.services.tool_workflow import (
    call_tool,
    run_trip_planner_workflow,
)


def test_call_tool_runs_planner():
    result = call_tool(
        "planner_tool",
        origin="Ha Noi",
        destination="Da Nang",
        soc_current=0.85,
        soc_comfort=0.20,
    )
    assert result["feasible"] is True
    assert "stops" in result


def test_call_tool_runs_validator():
    workflow = run_trip_planner_workflow("Ha Noi", "Da Nang", 0.85, 0.20)
    validation = workflow["validation_result"]
    assert validation["stop_count"] == len(workflow["plan_result"]["stops"])
    assert validation["is_consistent"] is True


def test_workflow_returns_plan_validation_and_summary():
    workflow = run_trip_planner_workflow("Ha Noi", "Da Nang", 0.85, 0.20)
    assert "plan_result" in workflow
    assert "validation_result" in workflow
    assert "summary_text" in workflow
