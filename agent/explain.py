from typing import List
from agent.geometry import TransportMode

def explain_recommendation(
    city: str,
    mode: TransportMode,
    score: float,
    reasons: List[str],
    precipitation: float,
) -> str:
    lines = []

    lines.append(f"For your trip to {city}, the agent recommends **{mode.value}**.")

    # Score-based reasoning
    lines.append(
        f"This option achieved the lowest overall planning score ({score:.2f}), "
        "indicating a good balance between travel efficiency and daily workload."
    )

    # Constraint reasoning
    if reasons:
        lines.append(
            "Some soft constraints were considered during planning:"
        )
        for r in reasons:
            lines.append(f"- {r}")
    else:
        lines.append(
            "All days satisfy the distance and experience constraints comfortably."
        )

    # Weather reasoning
    if precipitation >= 5:
        lines.append(
            f"Weather note: Expected precipitation is {precipitation:.1f} mm. "
            "This makes walking less comfortable, so motorized transport is preferred."
        )
    elif precipitation > 0:
        lines.append(
            f"Weather note: Light rain expected ({precipitation:.1f} mm). "
            "Some outdoor walking is fine, but flexibility is advised."
        )
    else:
        lines.append(
            "Weather note: No significant rainfall expected, suitable for outdoor activities."
        )

    return "\n".join(lines)
