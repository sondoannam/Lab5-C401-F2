def pct(value: float) -> str:
    return f"{round(value * 100)}%"


def minutes_to_text(total_minutes: int) -> str:
    hours, minutes = divmod(total_minutes, 60)
    if hours == 0:
        return f"{minutes} min"
    if minutes == 0:
        return f"{hours}h"
    return f"{hours}h {minutes}m"
