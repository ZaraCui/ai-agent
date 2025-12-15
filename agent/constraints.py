from dataclasses import dataclass
from typing import List, Tuple

from agent.types import Itinerary, Spot
from agent.geometry import TransportMode, travel_cost_minutes


@dataclass(frozen=True)
class ScoreConfig:
    # Max allowed travel time per day (minutes), by transport mode
    max_daily_minutes: dict

    # Penalty per exceeded minute
    exceed_minute_penalty: float = 1.5

    # Penalize days with too few spots
    one_spot_day_penalty: float = 15.0

    # Minimum expected spots per day (soft)
    min_spots_per_day: int = 2


def score_itinerary(
    itinerary: Itinerary,
    cfg: ScoreConfig,
    mode: TransportMode
) -> Tuple[float, List[str]]:
    """
    Lower score is better.
    Returns: (score, reasons)
    """
    reasons: List[str] = []

    total_spots = sum(len(day.spots) for day in itinerary.days)
    days = len(itinerary.days)
    expect_min = total_spots >= days * cfg.min_spots_per_day

    score = 0.0

    for day in itinerary.days:
        # ---- compute travel time for the day ----
        day_minutes = 0.0
        for i in range(len(day.spots) - 1):
            day_minutes += travel_cost_minutes(
                day.spots[i],
                day.spots[i + 1],
                mode
            )

        # Base objective: minimize total travel time
        score += day_minutes

        # ---- soft time constraint ----
        limit = cfg.max_daily_minutes[mode]
        if day_minutes > limit:
            exceed = day_minutes - limit
            penalty = exceed * cfg.exceed_minute_penalty
            score += penalty
            reasons.append(
                f"Day {day.day}: exceeded {limit:.0f} min by {exceed:.1f} (+{penalty:.1f})"
            )

        # ---- experience constraint ----
        if expect_min and len(day.spots) < cfg.min_spots_per_day:
            score += cfg.one_spot_day_penalty
            reasons.append(
                f"Day {day.day}: only {len(day.spots)} spot(s) (+{cfg.one_spot_day_penalty:.1f})"
            )

    return score, reasons
