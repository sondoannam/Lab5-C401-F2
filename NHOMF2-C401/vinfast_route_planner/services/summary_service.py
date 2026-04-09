import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Load 1 lần lúc import, không đọc lại mỗi request
_SYSTEM_PROMPT = (Path(__file__).parent / "system_prompt.txt").read_text(encoding="utf-8")

# OpenRouter dùng giao thức OpenAI → chỉ đổi base_url
_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", "dummy_key_for_testing"),
)
_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")


def _station_label(p_kw: float) -> str:
    """Map station power to the charging label used in summaries."""
    if p_kw >= 150:
        return "VinFast Super Charging Hub"
    elif p_kw >= 60:
        return "Fast DC Charging Station"
    return "Standard Charging Station"


import streamlit as st

def format_planner_output_for_llm(data: dict) -> str:
    """Convert planner output into plain text for the LLM."""
    lines = []
    stops = data.get("stops", [])
    total_charge_min = sum(stop.get("charge_min", 0) for stop in stops)
    total_drive_min = max(data["total_time_min"] - total_charge_min, 0)

    lines.append(f"STATUS: {'Feasible' if data['feasible'] else 'INFEASIBLE'}")
    lines.append(f"PLANNED SAFETY BUFFER: {round(data['soc_comfort'] * 100)}%")
    lines.append(f"ABSOLUTE MINIMUM BUFFER: {round(data['soc_hard'] * 100)}%")
    lines.append(f"ESTIMATED TOTAL TRIP TIME: {data['total_time_min']} minutes")
    lines.append(f"TOTAL DRIVE TIME: {total_drive_min} minutes")
    lines.append(f"TOTAL CHARGING TIME: {total_charge_min} minutes")
    lines.append(f"NUMBER OF CHARGING STOPS: {len(stops)}")
    lines.append("")

    if stops:
        for i, stop in enumerate(stops, 1):
            st_station = stop["station"]
            soc_arrive_pct = round(stop["soc_arrive"] * 100)
            soc_depart_pct = round(stop["soc_depart"] * 100)
            soc_comfort_pct = round(data["soc_comfort"] * 100)
            soc_hard_pct = round(data["soc_hard"] * 100)

            if soc_arrive_pct >= soc_comfort_pct:
                warning_tag = "OK"
            elif soc_arrive_pct >= soc_hard_pct:
                warning_tag = "YELLOW WARNING"
            else:
                warning_tag = "VIOLATION"

            amenities_str = st_station.get("amenities_text") or (
                ", ".join(st_station.get("amenities", [])) or "no amenity information"
            )
            charge_line = (
                f"Charge to: {soc_depart_pct}% (~{stop['charge_min']} minutes)"
                if soc_depart_pct > soc_arrive_pct and stop["charge_min"] > 0
                else "No additional charging needed"
            )

            lines.append(
                f"\nSTOP {i}: {st_station['name']} [{_station_label(st_station['p_station_kw'])}, {st_station['p_station_kw']} kW]"
            )
            lines.append(
                f"  Distance from previous point: {stop['distance_from_prev_km']} km (~{stop['drive_min_from_prev']} drive minutes)"
            )
            lines.append(f"  SoC on arrival: {soc_arrive_pct}% [{warning_tag}]")
            lines.append(f"  {charge_line}")
            lines.append(f"  Amenities: {amenities_str}")
    else:
        lines.append("NUMBER OF CHARGING STOPS: 0 (vehicle can reach the destination without charging)")

    warnings = data.get("warnings", [])
    if warnings:
        lines.append("\nSYSTEM WARNINGS:")
        for w in warnings:
            lines.append(f"  - {w}")

    return "\n".join(lines)


@st.cache_data(show_spinner=False)
def generate_summary(plan_result: dict) -> str:
    """Call the LLM via OpenRouter and return a Markdown trip summary."""
    user_message = format_planner_output_for_llm(plan_result)

    if not os.getenv("OPENROUTER_API_KEY"):
        return (
            "⚠️ **WARNING: `OPENROUTER_API_KEY` is not configured in the environment or `.env` file. "
            "Below is the raw planner payload (not yet summarized by the LLM):**\n\n"
            f"```text\n{user_message}\n```"
        )

    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"🔴 **LLM service connection error:** {str(e)}\n\n```text\n{user_message}\n```"
