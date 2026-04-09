import json
import streamlit as st

from vinfast_route_planner.core.config import STATIONS_FILE
from vinfast_route_planner.core.models import Station


@st.cache_data
def load_station_dataset() -> dict:
    with open(STATIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data
def load_metadata() -> dict:
    return load_station_dataset().get("metadata", {})


@st.cache_data
def load_stations() -> list[Station]:
    raw_stations = load_station_dataset().get("stations", [])
    return [
        Station(
            id=station["id"],
            name=station["name"],
            lat=station["lat"],
            lon=station["lon"],
            p_station_kw=station["p_station_kw"],
            type=station.get("type", "DC"),
            amenities=station.get("amenities", []),
            available_slots=station.get("available_slots", 0),
            setup_time_min=station.get("setup_time_min", 0),
            status=station.get("status", "active"),
        )
        for station in raw_stations
    ]


def filter_active_stations(stations: list[Station]) -> list[Station]:
    return [
        station
        for station in stations
        if station.status == "active" and station.available_slots > 0
    ]


def get_station_by_name(name: str) -> Station | None:
    return next((station for station in load_stations() if station.name == name), None)


def list_station_names() -> list[str]:
    return [station.name for station in load_stations()]
