from agent.planner import nearest_neighbor_path
from agent.types import Itinerary


def replan_single_day(itinerary: Itinerary, day_index: int) -> None:
    """
    Reorder spots within a single day to minimize travel distance.
    Modifies itinerary in-place.
    """
    day = itinerary.days[day_index]

    if len(day.spots) <= 2:
        return  # nothing to improve

    day.spots = nearest_neighbor_path(day.spots)
