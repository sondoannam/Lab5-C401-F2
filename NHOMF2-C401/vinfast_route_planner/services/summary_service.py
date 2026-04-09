def generate_summary(plan_result: dict) -> str:
    if not plan_result["feasible"]:
        return (
            "Route khong kha thi voi muc pin hien tai va buffer an toan. "
            "Hay tang SoC truoc khi khoi hanh hoac chon diem den gan hon."
        )

    stop_count = len(plan_result["stops"])
    warnings = plan_result["warnings"]
    warning_text = " Co canh bao: " + "; ".join(warnings) if warnings else ""
    return (
        f"Hanh trinh kha thi voi {stop_count} diem dung sac. "
        f"Tong thoi gian uoc tinh la {plan_result['total_time_min']} phut. "
        f"SoC luon duoc giu tren nguong hard {int(plan_result['soc_hard'] * 100)}%."
        f"{warning_text}"
    )
