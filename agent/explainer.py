from datetime import timedelta, date
from agent.models import Itinerary
from agent.geometry import TransportMode
from agent.weather import get_weather

def explain_recommendation(
    itinerary: Itinerary,
    mode: TransportMode,
    score: float,
    reasons: list[str],
) -> str:
    lines = []

    lines.append(
        f"I recommend using **{mode.value}** as your primary transport mode."
    )

    lines.append(
        f"This plan achieves a total optimization score of {score:.2f}, "
        "which balances travel efficiency and daily comfort."
    )

    if reasons:
        lines.append("During planning, the agent identified the following considerations:")
        for r in reasons:
            lines.append(f"- {r}")
    else:
        lines.append(
            "All daily routes stay within comfortable limits, "
            "with no distance or time penalties."
        )

    for day in itinerary.days:
        if not day.spots:
            continue

        route = " → ".join(s.name for s in day.spots)

        lines.append(
            f"Day {day.day} route: {route}"
        )
        lines.append(
            f"  Estimated travel distance: {day.total_distance_km:.1f} km"
        )

    return "\n".join(lines)


def weather_advice(itinerary: Itinerary, start_date: date) -> str:
    MAX_FORECAST_DAYS = 10  # conservative
    today = date.today()
    if (start_date - today).days < 0 or (start_date - today).days >= MAX_FORECAST_DAYS:
        return "⚠️ Weather forecast is unavailable for the selected dates."
    lines = []
    lines.append("🌦 Weather-aware advice:")

    for day in itinerary.days:
        if not day.spots:
            continue

        # Use the first spot as representative location
        lat = day.spots[0].lat
        lon = day.spots[0].lon

        precipitation = get_weather(lat, lon)

        idx = day.day - 1
        if idx >= len(precipitation):
            continue

        actual_date = start_date + timedelta(days=idx)
        rain_mm = precipitation[idx]

        if rain_mm > 5:
            lines.append(
                f"- {actual_date} (Day {day.day}): Heavy rain (~{rain_mm:.1f}mm). "
                "Consider minimizing walking or reordering indoor attractions."
            )
        elif rain_mm > 1:
            lines.append(
                f"- {actual_date} (Day {day.day}): Light rain (~{rain_mm:.1f}mm). "
                "A rain jacket is recommended."
            )
        else:
            lines.append(
                f"- {actual_date} (Day {day.day}): Clear or dry conditions. "
                "Ideal for walking routes."
            )

    return "\n".join(lines)
