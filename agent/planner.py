import math
import random
from copy import deepcopy
from typing import List, Tuple

from agent.models import Spot, DayPlan, Itinerary
from agent.constraints import ScoreConfig, score_itinerary
from agent.geometry import distance
from agent.geometry import TransportMode

def nearest_neighbor_path(spots: List[Spot]) -> List[Spot]:
    if not spots:
        return []

    unvisited = spots[:]
    path = [unvisited.pop(0)]

    while unvisited:
        last = path[-1]
        nxt = min(unvisited, key=lambda s: distance(last, s))
        path.append(nxt)
        unvisited.remove(nxt)

    return path


def build_initial_itinerary(city: str, spots: List[Spot], days: int) -> Itinerary:
    spots_sorted = sorted(spots, key=lambda s: (s.lon, s.lat))

    chunks: List[List[Spot]] = [[] for _ in range(days)]
    for i, s in enumerate(spots_sorted):
        chunks[i % days].append(s)

    day_plans: List[DayPlan] = []
    for i in range(days):
        ordered = nearest_neighbor_path(chunks[i])
        day_plans.append(
            DayPlan(day=i + 1, spots=ordered, total_distance_km=0.0)
        )

    return Itinerary(city=city, days=day_plans)

from agent.models import Itinerary
from agent.geometry import distance


def finalize_itinerary_distances(itinerary: Itinerary) -> None:
    """
    Compute and store total distance for each day.
    This should be called ONCE after the best itinerary is selected.
    """
    for day in itinerary.days:
        total = 0.0
        for i in range(len(day.spots) - 1):
            total += distance(day.spots[i], day.spots[i + 1])
        day.total_distance_km = round(total, 2)


def try_move_one_spot(itin: Itinerary) -> Itinerary:
    new_itin = deepcopy(itin)
    days = new_itin.days

    from_candidates = [d for d in days if len(d.spots) >= 2]
    if not from_candidates:
        return new_itin

    src = random.choice(from_candidates)
    dst = random.choice([d for d in days if d.day != src.day])

    idx = random.randrange(len(src.spots))
    moved = src.spots.pop(idx)
    dst.spots.append(moved)

    src.spots = nearest_neighbor_path(src.spots)
    dst.spots = nearest_neighbor_path(dst.spots)

    return new_itin


def try_swap_spots_between_days(itin: Itinerary) -> Itinerary:
    new_itin = deepcopy(itin)
    days = new_itin.days
    if len(days) < 2:
        return new_itin

    d1, d2 = random.sample(days, 2)
    if not d1.spots or not d2.spots:
        return new_itin

    i = random.randrange(len(d1.spots))
    j = random.randrange(len(d2.spots))

    d1.spots[i], d2.spots[j] = d2.spots[j], d1.spots[i]

    d1.spots = nearest_neighbor_path(d1.spots)
    d2.spots = nearest_neighbor_path(d2.spots)

    return new_itin


def plan_itinerary_soft_constraints(
    city: str,
    spots: List[Spot],
    days: int,
    cfg: ScoreConfig,
    mode: TransportMode,
    trials: int = 200,
) -> Tuple[Itinerary, float, List[str]]:

    random.seed(0)

    base = build_initial_itinerary(city, spots, days)
    best = base
    best_score, best_reasons = score_itinerary(best, cfg, mode)

    current = base
    for _ in range(trials):
        if random.random() < 0.6:
            candidate = try_move_one_spot(current)
        else:
            candidate = try_swap_spots_between_days(current)

        candidate_score, candidate_reasons = score_itinerary(candidate, cfg, mode)

        if candidate_score < best_score:
            best = candidate
            best_score = candidate_score
            best_reasons = candidate_reasons
            current = candidate

    return best, best_score, best_reasons
