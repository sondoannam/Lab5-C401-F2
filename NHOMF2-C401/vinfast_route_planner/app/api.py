import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from vinfast_route_planner.core.config import DEFAULT_DESTINATION, DEFAULT_ORIGIN, VEHICLE
from vinfast_route_planner.core.route_planner import resolve_location_coords
from vinfast_route_planner.services.tool_workflow import run_trip_planner_workflow
from vinfast_route_planner.utils.data_loader import list_station_names

app = FastAPI(title="VinFast Route Planner API")

# CORS middleware for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlanRequest(BaseModel):
    origin: str
    destination: str
    soc_current: float
    soc_comfort: float

from vinfast_route_planner.utils.data_loader import list_station_names, load_stations

@app.get("/api/stations")
def get_stations():
    return {"stations": list_station_names()}

@app.get("/api/stations/all")
def get_all_stations():
    stations = load_stations()
    return {"stations": [s.__dict__ for s in stations]}

@app.post("/api/plan")
def plan_route(req: PlanRequest):
    try:
        workflow_result = run_trip_planner_workflow(
            origin=req.origin,
            destination=req.destination,
            soc_current=req.soc_current / 100.0,
            soc_comfort=req.soc_comfort / 100.0,
            include_geometry=True,
        )
        # Bổ sung toạ độ start/end vào response để map vẽ marker dễ dàng
        origin_coords = resolve_location_coords(req.origin)
        destination_coords = resolve_location_coords(req.destination)
        
        workflow_result["coords"] = {
            "origin": {"lat": origin_coords[0], "lon": origin_coords[1]} if origin_coords else None,
            "destination": {"lat": destination_coords[0], "lon": destination_coords[1]} if destination_coords else None,
        }
        
        return workflow_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

from vinfast_route_planner.services.agent_service import chat_with_agent

@app.post("/api/chat")
def agent_chat(req: ChatRequest):
    try:
        # Convert Pydantic models to dicts
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in req.messages]
        result = chat_with_agent(messages_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

