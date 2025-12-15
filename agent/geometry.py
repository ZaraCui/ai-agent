import math
from agent.types import Spot

def distance(a: Spot, b: Spot) -> float:
    """
    Rough distance in km using lat/lon approximation.
    """
    return math.sqrt((a.lat - b.lat) ** 2 + (a.lon - b.lon) ** 2) * 111
