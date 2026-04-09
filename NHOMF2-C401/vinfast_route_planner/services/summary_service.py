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
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")


def _station_label(p_kw: float) -> str:
    """Phân loại trạm theo công suất, dùng đúng thuật ngữ VinFast."""
    if p_kw >= 150:
        return "Siêu trạm sạc VinFast"
    elif p_kw >= 60:
        return "Trạm sạc nhanh DC"
    return "Trạm sạc tiêu chuẩn"


def format_planner_output_for_llm(data: dict) -> str:
    """Chuyển dict của plan_route() thành plain text để đưa vào LLM."""
    lines = []

    lines.append(f"TRẠNG THÁI: {'Khả thi' if data['feasible'] else 'KHÔNG khả thi'}")
    lines.append(f"BUFFER AN TOÀN KẾ HOẠCH: {round(data['soc_comfort'] * 100)}%")
    lines.append(f"NGƯỠNG TUYỆT ĐỐI (SoC_hard): {round(data['soc_hard'] * 100)}%")
    lines.append(f"TỔNG THỜI GIAN ƯỚC TÍNH: {data['total_time_min']} phút")
    lines.append("")

    stops = data.get("stops", [])
    if stops:
        lines.append(f"SỐ ĐIỂM DỪNG SẠC: {len(stops)}")
        for i, stop in enumerate(stops, 1):
            st = stop["station"]
            soc_arrive_pct = round(stop["soc_arrive"] * 100)
            soc_depart_pct = round(stop["soc_depart"] * 100)
            soc_comfort_pct = round(data["soc_comfort"] * 100)
            soc_hard_pct = round(data["soc_hard"] * 100)

            # 3 mức cảnh báo theo spec
            if soc_arrive_pct >= soc_comfort_pct:
                warning_tag = "OK"
            elif soc_arrive_pct >= soc_hard_pct:
                warning_tag = "CẢNH BÁO VÀNG - buffer mỏng"
            else:
                warning_tag = "VI PHẠM SoC_hard"

            amenities_str = ", ".join(st.get("amenities", [])) or "không có thông tin"

            lines.append(f"\nĐIỂM DỪNG {i}: {st['name']} [{_station_label(st['p_station_kw'])}, {st['p_station_kw']} kW]")
            lines.append(f"  Khoảng cách từ điểm trước: {stop['distance_from_prev_km']} km (~{stop['drive_min_from_prev']} phút lái)")
            lines.append(f"  SoC khi đến: {soc_arrive_pct}% [{warning_tag}]")
            lines.append(f"  Sạc lên: {soc_depart_pct}% (~{stop['charge_min']} phút)")
            lines.append(f"  Tiện ích: {amenities_str}")
    else:
        lines.append("SỐ ĐIỂM DỪNG SẠC: 0 (xe đến đích không cần dừng sạc)")

    warnings = data.get("warnings", [])
    if warnings:
        lines.append("\nCẢNH BÁO TỪ HỆ THỐNG:")
        for w in warnings:
            lines.append(f"  - {w}")

    return "\n".join(lines)


def generate_summary(plan_result: dict) -> str:
    """Gọi LLM qua OpenRouter, trả Markdown tóm tắt hành trình."""
    user_message = format_planner_output_for_llm(plan_result)

    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content
