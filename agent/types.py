from pydantic import BaseModel
from typing import List
from enum import Enum

class TransportMode(str, Enum):
    WALK = "walk"
    TRANSIT = "transit"
    TAXI = "taxi"

class Spot(BaseModel):
    name: str
    lat: float
    lon: float
    category: str  # indoor / outdoor / food / museum / temple / shopping

class DayPlan(BaseModel):
    day: int
    spots: List[Spot]
    total_distance_km: float = 0.0

class Itinerary(BaseModel):
    city: str
    days: List[DayPlan]
