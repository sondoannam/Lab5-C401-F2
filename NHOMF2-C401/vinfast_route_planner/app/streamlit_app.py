import streamlit as st

from core.config import DEFAULT_DESTINATION, DEFAULT_ORIGIN, VEHICLE
from core.planner import plan_route
from services.summary_service import generate_summary
from utils.formatters import pct


st.set_page_config(page_title="VinFast Route Planner MVP", layout="wide")
st.title("VinFast Route Planner MVP")
st.caption(
    "Ban demo su dung du lieu tram va mo hinh tieu thu don gian, chi dung minh hoa."
)

with st.form("planner_form"):
    origin = st.text_input("Origin", value=DEFAULT_ORIGIN)
    destination = st.text_input("Destination", value=DEFAULT_DESTINATION)
    soc_current_pct = st.slider("Current SoC (%)", min_value=10, max_value=100, value=85)
    soc_comfort_pct = st.slider(
        "Comfort buffer (%)",
        min_value=15,
        max_value=40,
        value=int(VEHICLE["soc_comfort_default"] * 100),
    )
    submitted = st.form_submit_button("Plan route")

if submitted:
    result = plan_route(
        origin=origin,
        destination=destination,
        soc_current=soc_current_pct / 100,
        soc_comfort=soc_comfort_pct / 100,
    )
    st.subheader("Summary")
    st.write(generate_summary(result))

    if result["warnings"]:
        for warning in result["warnings"]:
            st.warning(warning)

    st.subheader("Stops")
    if result["stops"]:
        table_rows = []
        for stop in result["stops"]:
            table_rows.append(
                {
                    "Station": stop["station"]["name"],
                    "Drive km": stop["distance_from_prev_km"],
                    "Drive min": stop["drive_min_from_prev"],
                    "Arrive SoC": pct(stop["soc_arrive"]),
                    "Depart SoC": pct(stop["soc_depart"]),
                    "Charge min": stop["charge_min"],
                    "Amenities": ", ".join(stop["station"]["amenities"]),
                }
            )
        st.dataframe(table_rows, use_container_width=True)
    else:
        st.info("Khong co diem dung sac nao trong ke hoach hien tai.")

    st.metric("Total time", f"{result['total_time_min']} min")
