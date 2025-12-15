from agent.planner import nearest_neighbor_path
from agent.types import Itinerary
from agent.semantics import is_indoor,is_outdoor
from datetime import date

def replan_single_day(itinerary, day_idx):
    day = itinerary.days[day_idx]

    outdoor_spots = [s for s in day.spots if is_outdoor(s)]
    if not outdoor_spots:
        return False  # nothing to fix

    # Other day's indoor spot
    for other_day in itinerary.days:
        if other_day.day == day.day:
            continue

        indoor_candidates = [s for s in other_day.spots if is_indoor(s)]
        if indoor_candidates:
            # swap
            day.spots.remove(outdoor_spots[0])
            other_day.spots.remove(indoor_candidates[0])

            day.spots.append(indoor_candidates[0])
            other_day.spots.append(outdoor_spots[0])
            return True

    return False

def balance_day_plans(itinerary: Itinerary) -> Itinerary:
    """
    Rebalance the itinerary to avoid days with too few spots.
    Move spots from crowded days to sparse days.    
    """
    new_itin = deepcopy(itinerary)

    # Find days with only one spot
    single_spot_days = [d for d in new_itin.days if len(d.spots) == 1]
    
    # Find days with more than two spots    
    crowded_days = [d for d in new_itin.days if len(d.spots) > 2]

    # If no balancing needed, return original
    if not single_spot_days or not crowded_days:
        return new_itin

    # Solution: move one spot from crowded day to single spot day
    for day in single_spot_days:
        # Pick the first crowded day from which to move a spot to this single spot day
        target_day = crowded_days[0]  
        spot_to_move = target_day.spots.pop()  
        day.spots.append(spot_to_move)  

        # update the last if the crowded day is now balanced
        if len(target_day.spots) == 2:
            crowded_days.pop(0)  # remove balanced day

    return new_itin
