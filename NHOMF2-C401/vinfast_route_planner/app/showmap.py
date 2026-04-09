import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st
import folium
from streamlit_folium import st_folium

from vinfast_route_planner.core.config import DEFAULT_DESTINATION, DEFAULT_ORIGIN, VEHICLE
from vinfast_route_planner.core.route_planner import plan_route
from vinfast_route_planner.services.summary_service import generate_summary
from vinfast_route_planner.utils.formatters import pct


st.set_page_config(page_title="VinFast Route Planner MVP", layout="wide")

# ===== HEADER =====
st.title("🚗 VinFast EV Route Planner")
st.caption("Lập kế hoạch hành trình xe điện với trạm sạc tối ưu")

# ===== LAYOUT =====
col1, col2 = st.columns([1, 2])

# ===== LEFT: FORM =====
with col1:
    st.subheader("⚙️ Input")


    with st.form("planner_form"):
        origin = st.text_input("Origin", value=DEFAULT_ORIGIN)
        destination = st.text_input("Destination", value=DEFAULT_DESTINATION)

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
            result = plan_route(
                origin=origin,
                destination=destination,
                soc_current=soc_current_pct / 100,
                soc_comfort=soc_comfort_pct / 100,
            )
            st.session_state["result"] = result

    # ===== RENDER RESULT (LUÔN HIỂN THỊ) =====
    if "result" in st.session_state:
        result = st.session_state["result"]

        # ===== SUMMARY =====
        st.subheader("📊 Summary")

        colA, colB, colC = st.columns(3)
        colA.metric("Total Time", f"{result['total_time_min']} min")
        colB.metric("Stops", len(result["stops"]))
        colC.metric("Final SoC", pct(result.get("final_soc", 0)))

        st.write(generate_summary(result))

        # ===== WARNINGS =====
        if result["warnings"]:
            for warning in result["warnings"]:
                st.warning(warning)

        # ===== MAP =====
        st.subheader("🗺️ Route Map")

        if result.get("geometry"):
            coords = result["geometry"]["coordinates"]
            lat_lon_coords = [[c[1], c[0]] for c in coords]

            m = folium.Map(location=lat_lon_coords[0], zoom_start=6)

            # Route
            folium.PolyLine(
                lat_lon_coords,
                color="blue",
                weight=5
            ).add_to(m)

            # Start / End
            folium.Marker(lat_lon_coords[0], tooltip="Start").add_to(m)
            folium.Marker(lat_lon_coords[-1], tooltip="End").add_to(m)

            # Stops
            for stop in result["stops"]:
                lat = stop["station"]["lat"]
                lon = stop["station"]["lon"]

                folium.Marker(
                    [lat, lon],
                    tooltip=stop["station"]["name"],
                    icon=folium.Icon(color="green", icon="bolt")
                ).add_to(m)

            m.fit_bounds(lat_lon_coords)

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