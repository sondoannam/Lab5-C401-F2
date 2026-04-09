from typing import Any, Callable

from vinfast_route_planner.core.route_planner import plan_route
from vinfast_route_planner.services.summary_service import generate_summary


ToolFn = Callable[..., Any]


def planner_tool(
    origin: str,
    destination: str,
    soc_current: float,
    soc_comfort: float,
    include_geometry: bool = False,
) -> dict:
    return plan_route(
        origin=origin,
        destination=destination,
        soc_current=soc_current,
        soc_comfort=soc_comfort,
        include_geometry=include_geometry,
    )


def validate_plan_tool(plan_result: dict) -> dict:
    stops = plan_result.get("stops", [])
    total_charge_min = sum(stop.get("charge_min", 0) for stop in stops)
    total_drive_min = max(plan_result.get("total_time_min", 0) - total_charge_min, 0)
    invalid_stops = []

    for index, stop in enumerate(stops, start=1):
        if stop["soc_arrive"] >= stop["soc_depart"] and stop["charge_min"] > 0:
            invalid_stops.append(
                {
                    "stop_index": index,
                    "station_name": stop["station"]["name"],
                    "issue": "arrival_soc_not_below_depart_soc",
                }
            )

    return {
        "stop_count": len(stops),
        "total_drive_min": total_drive_min,
        "total_charge_min": total_charge_min,
        "has_warnings": bool(plan_result.get("warnings")),
        "invalid_stops": invalid_stops,
        "is_consistent": len(invalid_stops) == 0,
    }


def summary_tool(plan_result: dict, validation_result: dict) -> str:
    summary_input = dict(plan_result)
    summary_input["validation"] = validation_result
    return generate_summary(summary_input)


TOOLS: dict[str, ToolFn] = {
    "planner_tool": planner_tool,
    "validate_plan_tool": validate_plan_tool,
    "summary_tool": summary_tool,
}


def call_tool(tool_name: str, **kwargs) -> Any:
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")
    return TOOLS[tool_name](**kwargs)


def run_trip_planner_workflow(
    origin: str,
    destination: str,
    soc_current: float,
    soc_comfort: float,
    include_geometry: bool = False,
) -> dict:
    plan_result = call_tool(
        "planner_tool",
        origin=origin,
        destination=destination,
        soc_current=soc_current,
        soc_comfort=soc_comfort,
        include_geometry=include_geometry,
    )
    validation_result = call_tool("validate_plan_tool", plan_result=plan_result)
    summary_text = call_tool(
        "summary_tool",
        plan_result=plan_result,
        validation_result=validation_result,
    )

    return {
        "plan_result": plan_result,
        "validation_result": validation_result,
        "summary_text": summary_text,
    }
