import streamlit as st

from vinfast_route_planner.core.config import DEFAULT_DESTINATION, DEFAULT_ORIGIN, VEHICLE
from vinfast_route_planner.core.route_planner import plan_route
from vinfast_route_planner.services.summary_service import generate_summary
from vinfast_route_planner.utils.data_loader import list_station_names
from vinfast_route_planner.utils.formatters import minutes_to_text, pct


st.set_page_config(page_title="VinFast Route Planner MVP", layout="wide")
st.title("VinFast Route Planner MVP")
st.caption(
    "Ban demo su dung du lieu tram mock va mo hinh tieu thu don gian, chi de minh hoa."
)

station_names = list_station_names()
origin_options = [DEFAULT_ORIGIN, *station_names]
destination_options = [DEFAULT_DESTINATION, *station_names]

with st.form("planner_form"):
    st.subheader("Thong tin hanh trinh")
    col_origin, col_destination = st.columns(2)
    with col_origin:
        origin = st.selectbox(
            "Diem xuat phat",
            options=origin_options,
            index=origin_options.index(DEFAULT_ORIGIN),
        )
    with col_destination:
        destination = st.selectbox(
            "Diem den",
            options=destination_options,
            index=destination_options.index(DEFAULT_DESTINATION),
        )

    soc_current_pct = st.slider("Muc pin hien tai (%)", min_value=10, max_value=100, value=85)
    soc_comfort_pct = st.slider(
        "Muc pin du phong mong muon (%)",
        min_value=15,
        max_value=40,
        value=int(VEHICLE["soc_comfort_default"] * 100),
    )
    submitted = st.form_submit_button("Lap lo trinh")

if submitted:
    result = plan_route(
        origin=origin,
        destination=destination,
        soc_current=soc_current_pct / 100,
        soc_comfort=soc_comfort_pct / 100,
    )

    st.subheader("Tong quan lo trinh")
    if result["feasible"]:
        st.success(generate_summary(result))
    else:
        st.error(generate_summary(result))

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("Trang thai", "Kha thi" if result["feasible"] else "Khong kha thi")
    metric_2.metric("So diem dung sac", len(result["stops"]))
    metric_3.metric("Tong thoi gian du kien", minutes_to_text(result["total_time_min"]))

    st.subheader("Muc an toan")
    st.write(
        f"Nguong toi thieu: {pct(result['soc_hard'])} | Muc du phong da chon: {pct(result['soc_comfort'])}"
    )

    if result["warnings"]:
        st.subheader("Canh bao")
        for warning in result["warnings"]:
            st.warning(warning)

    st.subheader("Danh sach diem dung sac")
    if result["stops"]:
        table_rows = []
        for index, stop in enumerate(result["stops"], start=1):
            station = stop["station"]
            table_rows.append(
                {
                    "Diem dung": index,
                    "Tram sac": station["name"],
                    "Trang thai": station["status"],
                    "Cho trong": station["available_slots"],
                    "Quang duong (km)": stop["distance_from_prev_km"],
                    "Thoi gian lai xe": minutes_to_text(stop["drive_min_from_prev"]),
                    "Pin khi den": pct(stop["soc_arrive"]),
                    "Pin khi roi": pct(stop["soc_depart"]),
                    "Thoi gian sac": minutes_to_text(stop["charge_min"]),
                    "Cong suat (kW)": station["p_station_kw"],
                    "Tien ich": ", ".join(station["amenities"]),
                }
            )
        st.dataframe(table_rows, use_container_width=True)

        st.subheader("Chi tiet tung diem dung")
        for index, stop in enumerate(result["stops"], start=1):
            station = stop["station"]
            with st.container(border=True):
                st.markdown(f"**Diem dung {index}: {station['name']}**")
                st.write(
                    f"Di chuyen {stop['distance_from_prev_km']} km trong {minutes_to_text(stop['drive_min_from_prev'])}. "
                    f"Den noi voi muc pin {pct(stop['soc_arrive'])}, sac trong {minutes_to_text(stop['charge_min'])}, "
                    f"roi tram voi muc pin {pct(stop['soc_depart'])}."
                )
                st.write(
                    f"Cong suat tram: {station['p_station_kw']} kW | "
                    f"So cho trong: {station['available_slots']} | "
                    f"Tien ich: {', '.join(station['amenities'])}"
                )
    else:
        st.info("Khong co diem dung sac nao trong ke hoach hien tai.")

    with st.expander("Luu y demo", expanded=True):
        st.write(
            "Ban demo su dung du lieu tram mock, khong phai du lieu real-time. "
            "Ket qua chi la uoc tinh de minh hoa, khong dung cho hanh trinh thuc te."
        )
