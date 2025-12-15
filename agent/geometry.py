import math
from agent.types import Spot
from enum import Enum

def distance(a: Spot, b: Spot) -> float:
    """
    Rough distance in km using lat/lon approximation.
    """
    return math.sqrt((a.lat - b.lat) ** 2 + (a.lon - b.lon) ** 2) * 111

from enum import Enum
from agent.types import Spot

class TransportMode(str, Enum):
    WALK = "walk"
    TRANSIT = "transit"
    TAXI = "taxi"


def distance(a: Spot, b: Spot) -> float:
    """
    Rough distance in km.
    """
    return ((a.lat - b.lat) ** 2 + (a.lon - b.lon) ** 2) ** 0.5 * 111


def travel_cost_minutes(a: Spot, b: Spot, mode: TransportMode) -> float:
    """
    Travel cost in minutes depending on transport mode.
    """
    km = distance(a, b)

    if mode == TransportMode.WALK:
        speed_kmh = 4.5
        return (km / speed_kmh) * 60

    if mode == TransportMode.TRANSIT:
        speed_kmh = 20.0
        wait_time = 5.0
        return (km / speed_kmh) * 60 + wait_time

    if mode == TransportMode.TAXI:
        speed_kmh = 30.0
        return (km / speed_kmh) * 60

    raise ValueError(f"Unknown transport mode: {mode}")
