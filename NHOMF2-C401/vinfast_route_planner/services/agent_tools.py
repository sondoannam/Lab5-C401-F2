import json
from typing import Optional

from vinfast_route_planner.services.tool_workflow import run_trip_planner_workflow
from vinfast_route_planner.utils.data_loader import load_stations
from vinfast_route_planner.core.route_planner import resolve_location_coords

def plan_ev_route(origin: str, destination: str, current_soc: float, comfort_soc: float = 0.2) -> str:
    """
    Computes the fastest-safe EV route from Origin to Destination.
    Args:
        origin (str): Start location (e.g. 'Hà Nội')
        destination (str): End location (e.g. 'Đà Nẵng')
        current_soc (float): Current State of Charge (0.0 to 1.0 or percentage like 80)
        comfort_soc (float): Comfort buffer (0.0 to 1.0 or percentage like 20)
    Returns:
        JSON string of the route plan.
    """
    if current_soc > 1.0:
        current_soc = current_soc / 100.0
    if comfort_soc > 1.0:
        comfort_soc = comfort_soc / 100.0

    try:
        workflow_result = run_trip_planner_workflow(
            origin=origin,
            destination=destination,
            soc_current=current_soc,
            soc_comfort=comfort_soc,
            include_geometry=True,
        )
        # Extract meaningful info
        plan = workflow_result["plan_result"]
        feasible = plan.get("feasible", False)
        stops = plan.get("stops", [])
        warnings = plan.get("warnings", [])
        total_time_min = plan.get("total_time_min", 0)
        
        origin_coords = resolve_location_coords(origin)
        destination_coords = resolve_location_coords(destination)

        return json.dumps({
            "feasible": feasible,
            "total_time_min": total_time_min,
            "warnings": warnings,
            "number_of_stops": len(stops),
            "stops": [
                {
                    "station_id": stop["station"]["id"],
                    "station_name": stop["station"]["name"],
                    "soc_arrive": stop["soc_arrive"],
                    "charge_min": stop["charge_min"],
                    "soc_depart": stop["soc_depart"]
                } for stop in stops
            ],
            "coords": {
                "origin": {"lat": origin_coords[0], "lon": origin_coords[1]} if origin_coords else None,
                "destination": {"lat": destination_coords[0], "lon": destination_coords[1]} if destination_coords else None,
            },
            # Return full workflow result as well so we can pass it to frontend via metadata if needed
            "_raw_workflow_result": workflow_result
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def get_station_info(station_id: str) -> str:
    """
    Retrieves detailed metadata about a specific charging station.
    Args:
        station_id (str): ID of the station to lookup.
    """
    stations = load_stations()
    for s in stations:
        if s.id == station_id:
            return json.dumps(s.__dict__, ensure_ascii=False)
    return json.dumps({"error": f"Station with id {station_id} not found."})

# List of definitions for the LLM
AGENT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "plan_ev_route",
            "description": "Computes the fastest-safe EV route. Call this to generate a route plan and charging stops.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Start location (e.g. 'Hà Nội')"},
                    "destination": {"type": "string", "description": "End location (e.g. 'Đà Nẵng')"},
                    "current_soc": {"type": "number", "description": "Current State of Charge percentage (0 to 100)"},
                    "comfort_soc": {"type": "number", "description": "Comfort buffer percentage (default 20)"}
                },
                "required": ["origin", "destination", "current_soc"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_station_info",
            "description": "Retrieves detailed metadata (amenities, charging power, type) about a specific station.",
            "parameters": {
                "type": "object",
                "properties": {
                    "station_id": {"type": "string", "description": "ID of the station to lookup (e.g. 'vinh_01')"}
                },
                "required": ["station_id"]
            }
        }
    }
]

def execute_tool(name: str, arguments: dict):
    if name == "plan_ev_route":
        return plan_ev_route(**arguments)
    elif name == "get_station_info":
        return get_station_info(**arguments)
    else:
        return json.dumps({"error": f"Unknown tool: {name}"})
