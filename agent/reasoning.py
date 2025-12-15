def explain_weather_trigger(day: int, rain_mm: float) -> str:
    return (
        f"Day {day} is expected to have heavy rain (~{rain_mm:.1f}mm), "
        "which violates the assumption that this day is suitable for walking-intensive routes. "
        "Replanning is triggered to improve comfort."
    )
