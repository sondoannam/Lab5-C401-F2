from unittest.mock import MagicMock, patch

from vinfast_route_planner.services.summary_service import (
    _station_label,
    format_planner_output_for_llm,
    generate_summary,
)

# --- Fixtures ---

FEASIBLE_PLAN = {
    "feasible": True,
    "soc_comfort": 0.20,
    "soc_hard": 0.10,
    "total_time_min": 578,
    "warnings": [],
    "stops": [
        {
            "station": {
                "id": "ST_VI_05",
                "name": "Siêu trạm sạc VinFast TP. Vinh",
                "p_station_kw": 250,
                "type": "DC",
                "amenities": ["restaurant", "coffee", "wifi"],
            },
            "distance_from_prev_km": 291.5,
            "drive_min_from_prev": 233,
            "soc_arrive": 0.22,
            "soc_depart": 0.80,
            "charge_min": 50,
        },
        {
            "station": {
                "id": "ST_DH_09",
                "name": "Siêu trạm Vincom Đồng Hới",
                "p_station_kw": 150,
                "type": "DC",
                "amenities": ["shopping_mall", "coffee"],
            },
            "distance_from_prev_km": 189.3,
            "drive_min_from_prev": 151,
            "soc_arrive": 0.29,
            "soc_depart": 0.80,
            "charge_min": 38,
        },
    ],
}

INFEASIBLE_PLAN = {
    "feasible": False,
    "soc_comfort": 0.20,
    "soc_hard": 0.10,
    "total_time_min": 0,
    "warnings": ["Khong co tram sac kha dung tiep theo voi muc pin hien tai."],
    "stops": [],
}

YELLOW_WARNING_PLAN = {
    "feasible": True,
    "soc_comfort": 0.20,
    "soc_hard": 0.10,
    "total_time_min": 400,
    "warnings": ["Buffer mong khi den Tram Ha Tinh: 15%."],
    "stops": [
        {
            "station": {
                "id": "ST_HT_06",
                "name": "Trạm dừng nghỉ Hà Tĩnh",
                "p_station_kw": 30,
                "type": "DC",
                "amenities": ["restroom"],
            },
            "distance_from_prev_km": 340.0,
            "drive_min_from_prev": 272,
            "soc_arrive": 0.15,  # < soc_comfort(20%) but >= soc_hard(10%)
            "soc_depart": 0.80,
            "charge_min": 128,
        },
    ],
}


# --- _station_label ---

def test_station_label_sieu_tram():
    assert _station_label(250) == "VinFast Super Charging Hub"
    assert _station_label(150) == "VinFast Super Charging Hub"


def test_station_label_nhanh():
    assert _station_label(60) == "Fast DC Charging Station"
    assert _station_label(100) == "Fast DC Charging Station"


def test_station_label_tieu_chuan():
    assert _station_label(30) == "Standard Charging Station"
    assert _station_label(59) == "Standard Charging Station"


# --- format_planner_output_for_llm ---

def test_format_feasible_contains_status():
    text = format_planner_output_for_llm(FEASIBLE_PLAN)
    assert "STATUS: Feasible" in text


def test_format_infeasible_contains_status():
    text = format_planner_output_for_llm(INFEASIBLE_PLAN)
    assert "STATUS: INFEASIBLE" in text


def test_format_contains_stop_count():
    text = format_planner_output_for_llm(FEASIBLE_PLAN)
    assert "NUMBER OF CHARGING STOPS: 2" in text


def test_format_contains_station_names():
    text = format_planner_output_for_llm(FEASIBLE_PLAN)
    assert "Siêu trạm sạc VinFast TP. Vinh" in text
    assert "Siêu trạm Vincom Đồng Hới" in text


def test_format_contains_station_label():
    text = format_planner_output_for_llm(FEASIBLE_PLAN)
    assert "VinFast Super Charging Hub" in text


def test_format_ok_warning_tag():
    text = format_planner_output_for_llm(FEASIBLE_PLAN)
    # soc_arrive=22% >= soc_comfort=20% → OK
    assert "[OK]" in text


def test_format_yellow_warning_tag():
    text = format_planner_output_for_llm(YELLOW_WARNING_PLAN)
    assert "YELLOW WARNING" in text


def test_format_contains_amenities():
    text = format_planner_output_for_llm(FEASIBLE_PLAN)
    assert "restaurant" in text
    assert "coffee" in text
    assert "wifi" in text


def test_format_contains_system_warnings():
    text = format_planner_output_for_llm(YELLOW_WARNING_PLAN)
    assert "SYSTEM WARNINGS" in text
    assert "Buffer mong khi den Tram Ha Tinh" in text


def test_format_no_stops_message():
    text = format_planner_output_for_llm(INFEASIBLE_PLAN)
    assert "NUMBER OF CHARGING STOPS: 0" in text


def test_format_contains_total_time():
    text = format_planner_output_for_llm(FEASIBLE_PLAN)
    assert "578 minutes" in text


# --- generate_summary (mocked) ---

@patch("vinfast_route_planner.services.summary_service._client")
def test_generate_summary_calls_llm(mock_client):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Lộ trình ổn, dừng sạc tại Vinh."
    mock_client.chat.completions.create.return_value = mock_response

    result = generate_summary(FEASIBLE_PLAN)

    assert result == "Lộ trình ổn, dừng sạc tại Vinh."
    mock_client.chat.completions.create.assert_called_once()


@patch("vinfast_route_planner.services.summary_service._client")
def test_generate_summary_passes_system_prompt(mock_client):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "OK"
    mock_client.chat.completions.create.return_value = mock_response

    generate_summary(FEASIBLE_PLAN)

    call_kwargs = mock_client.chat.completions.create.call_args
    messages = call_kwargs.kwargs.get("messages") or call_kwargs.args[0]
    roles = [m["role"] for m in messages]
    assert "system" in roles


@patch("vinfast_route_planner.services.summary_service._client")
def test_generate_summary_user_message_contains_plan(mock_client):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "OK"
    mock_client.chat.completions.create.return_value = mock_response

    generate_summary(FEASIBLE_PLAN)

    call_kwargs = mock_client.chat.completions.create.call_args
    messages = call_kwargs.kwargs.get("messages") or call_kwargs.args[0]
    user_msg = next(m["content"] for m in messages if m["role"] == "user")
    assert "Feasible" in user_msg
    assert "578 minutes" in user_msg
