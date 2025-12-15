from dataclasses import dataclass
from typing import List, Tuple

from agent.types import Itinerary, Spot
from agent.geometry import distance

@dataclass(frozen=True)
class ScoreConfig:
    # Soft upper bound for daily distance (km)
    max_daily_km: float = 6.0

    # Penalty per km when exceeding max_daily_km
    exceed_km_penalty: float = 25.0

    # Penalize days with too few spots when total spots allow better distribution
    one_spot_day_penalty: float = 15.0

    # Minimum expected spots per day (soft, via penalty)
    min_spots_per_day: int = 2


def compute_day_distance_km(spots: List[Spot]) -> float:
    total = 0.0
    for i in range(len(spots) - 1):
        total += distance(spots[i], spots[i + 1])
    return total


def score_itinerary(itinerary: Itinerary, cfg: ScoreConfig) -> Tuple[float, List[str]]:
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
        day_km = compute_day_distance_km(day.spots)
        day.total_distance_km = round(day_km, 2)

        # Base objective: shorter routes are better
        score += day_km

        # Soft constraint: exceeding daily distance
        if day_km > cfg.max_daily_km:
            exceed = day_km - cfg.max_daily_km
            penalty = exceed * cfg.exceed_km_penalty
            score += penalty
            reasons.append(
                f"Day {day.day}: exceeded {cfg.max_daily_km:.1f}km by {exceed:.2f}km (+{penalty:.2f})"
            )

        # Experience penalty: too few spots in a day
        if expect_min and len(day.spots) < cfg.min_spots_per_day:
            score += cfg.one_spot_day_penalty
            reasons.append(
                f"Day {day.day}: only {len(day.spots)} spot(s) (+{cfg.one_spot_day_penalty:.2f})"
            )

    return score, reasons
