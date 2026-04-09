def pct(value: float) -> str:
    return f"{round(value * 100)}%"


def minutes_to_text(total_minutes: int) -> str:
    hours, minutes = divmod(total_minutes, 60)
    if hours == 0:
        return f"{minutes} min"
    if minutes == 0:
        return f"{hours}h"
    return f"{hours}h {minutes}m"


AMENITY_TRANSLATIONS = {
    "shopping_mall": "Trung tâm thương mại",
    "coffee": "Cà phê",
    "restroom": "Nhà vệ sinh",
    "restaurant": "Nhà hàng",
    "cinema": "Rạp chiếu phim",
    "wifi": "WiFi miễn phí",
    "parking": "Bãi đậu xe",
    "tourist_info": "Trạm thông tin du lịch",
    "scenic_view": "Trạm dừng ngắm cảnh",
    "hotel": "Khách sạn nghỉ ngơi",
}


def format_amenities_for_llm(amenities: list[str]) -> str:
    """Translates raw amenity codes to user-friendly messages for the AI summary."""
    if not amenities:
        return ""
        
    translated = [AMENITY_TRANSLATIONS.get(item.lower(), item.capitalize()) for item in amenities]
    
    return f"Dừng ở đây có {', '.join(translated)} cho bạn nghỉ ngơi."
