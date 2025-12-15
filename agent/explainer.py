from agent.types import Itinerary
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

    # Explain score
    lines.append(
        f"This plan achieves a total optimization score of {score:.2f}, "
        "which balances travel efficiency and daily comfort."
    )

    # Explain constraints
    if reasons:
        lines.append("During planning, the agent identified the following considerations:")
        for r in reasons:
            lines.append(f"- {r}")
    else:
        lines.append(
            "All daily routes stay within comfortable limits, "
            "with no distance or time penalties."
        )

    # Day-level explanation
    for day in itinerary.days:
        lines.append(
            f"Day {day.day} includes {len(day.spots)} locations "
            f"with an estimated travel distance of {day.total_distance_km:.1f} km."
        )

    return "\n".join(lines)

def weather_advice(itinerary: Itinerary) -> str:
    lines = []
    lines.append("🌦 Weather-aware advice:")

    for day in itinerary.days:
        if not day.spots:
            continue

        # Use first spot as representative location
        lat = day.spots[0].lat
        lon = day.spots[0].lon

        precipitation = get_weather(lat, lon)

        # precipitation is a list (one per day)
        rain_mm = precipitation[min(day.day - 1, len(precipitation) - 1)]

        if rain_mm > 5:
            lines.append(
                f"- Day {day.day}: Heavy rain expected (~{rain_mm:.1f}mm). "
                "Consider minimizing walking or reordering indoor attractions."
            )
        elif rain_mm > 1:
            lines.append(
                f"- Day {day.day}: Light rain expected (~{rain_mm:.1f}mm). "
                "A rain jacket is recommended."
            )
        else:
            lines.append(
                f"- Day {day.day}: Clear or dry conditions. Ideal for walking routes."
            )

    return "\n".join(lines)

