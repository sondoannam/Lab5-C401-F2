import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st
import folium
from streamlit_folium import st_folium

from vinfast_route_planner.core.config import DEFAULT_DESTINATION, DEFAULT_ORIGIN, VEHICLE
from vinfast_route_planner.core.route_planner import resolve_location_coords
from vinfast_route_planner.services.tool_workflow import run_trip_planner_workflow
from vinfast_route_planner.utils.data_loader import list_station_names
from vinfast_route_planner.utils.formatters import pct


st.set_page_config(page_title="VinFast Route Planner MVP", layout="wide")

# ===== HEADER =====
st.title("🚗 VinFast EV Route Planner")
st.caption("Lập kế hoạch hành trình xe điện với trạm sạc tối ưu")

station_names = list_station_names()
origin_options = [DEFAULT_ORIGIN, *station_names]
destination_options = [DEFAULT_DESTINATION, *station_names]

# ===== LAYOUT =====
col1, col2 = st.columns([1, 2])

# ===== LEFT: FORM =====
with col1:
    st.subheader("⚙️ Input")


    with st.form("planner_form"):
        origin = st.selectbox("Origin", options=origin_options, index=origin_options.index(DEFAULT_ORIGIN))
        destination = st.selectbox("Destination", options=destination_options, index=destination_options.index(DEFAULT_DESTINATION))

        soc_current_pct = st.slider("🔋 Current SoC (%)", 10, 100, 85)
        soc_comfort_pct = st.slider(
            "🛡️ Comfort buffer (%)",
            15,
            40,
            int(VEHICLE["soc_comfort_default"] * 100),
        )

        submitted = st.form_submit_button("🚀 Plan route")


# ===== RIGHT: RESULT =====
with col2:

    # ===== HANDLE SUBMIT =====
    if submitted:
        with st.spinner("🚀 Đang tính toán route..."):
            workflow_result = run_trip_planner_workflow(
                origin=origin,
                destination=destination,
                soc_current=soc_current_pct / 100,
                soc_comfort=soc_comfort_pct / 100,
            )
            st.session_state["workflow_result"] = workflow_result

    # ===== RENDER RESULT (LUÔN HIỂN THỊ) =====
    if "workflow_result" in st.session_state:
        workflow_result = st.session_state["workflow_result"]
        result = workflow_result["plan_result"]
        validation = workflow_result["validation_result"]
        summary_text = workflow_result["summary_text"]

        # ===== SUMMARY =====
        st.subheader("📊 Summary")

        colA, colB, colC = st.columns(3)
        colA.metric("Total Time", f"{result['total_time_min']} min")
        colB.metric("Stops", len(result["stops"]))
        final_soc = result["stops"][-1]["soc_depart"] if result["stops"] else 0
        colC.metric("Last stop depart SoC", pct(final_soc))

        st.write(summary_text)
        st.caption(
            f"Tool flow: planner_tool -> validate_plan_tool -> summary_tool | Validation: {'OK' if validation['is_consistent'] else 'Needs review'}"
        )

        # ===== WARNINGS =====
        if result["warnings"]:
            for warning in result["warnings"]:
                st.warning(warning)

        # ===== MAP =====
        st.subheader("🗺️ Route Map")
        origin_coords = resolve_location_coords(origin)
        destination_coords = resolve_location_coords(destination)
        map_points = []
        if origin_coords:
            map_points.append([origin_coords[0], origin_coords[1]])
        for stop in result["stops"]:
            map_points.append([stop["station"]["lat"], stop["station"]["lon"]])
        if destination_coords:
            map_points.append([destination_coords[0], destination_coords[1]])

        if map_points:
            m = folium.Map(location=map_points[0], zoom_start=6)
            folium.PolyLine(map_points, color="blue", weight=5).add_to(m)
            if origin_coords:
                folium.Marker(
                    [origin_coords[0], origin_coords[1]],
                    tooltip=f"Start: {origin}",
                    icon=folium.Icon(color="blue", icon="play"),
                ).add_to(m)
            if destination_coords:
                folium.Marker(
                    [destination_coords[0], destination_coords[1]],
                    tooltip=f"Destination: {destination}",
                    icon=folium.Icon(color="red", icon="flag"),
                ).add_to(m)
            for stop in result["stops"]:
                folium.Marker(
                    [stop["station"]["lat"], stop["station"]["lon"]],
                    tooltip=stop["station"]["name"],
                    icon=folium.Icon(color="green", icon="bolt"),
                ).add_to(m)
            m.fit_bounds(map_points)
            st_folium(m, width=900, height=450)
        else:
            st.warning("⚠️ Không có dữ liệu bản đồ")

        # ===== STOPS TABLE =====
        st.subheader("⚡ Charging Stops")

        if result["stops"]:
            table_rows = []
            for stop in result["stops"]:
                table_rows.append(
                    {
                        "Station": stop["station"]["name"],
                        "Drive (km)": stop["distance_from_prev_km"],
                        "Time (min)": stop["drive_min_from_prev"],
                        "Arrive SoC": pct(stop["soc_arrive"]),
                        "Depart SoC": pct(stop["soc_depart"]),
                        "Charge (min)": stop["charge_min"],
                    }
                )

            st.dataframe(table_rows, width="stretch")
        else:
            st.success("🎉 Không cần sạc — đủ pin đến đích!")
