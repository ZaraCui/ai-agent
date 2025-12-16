from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional
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
    # optional metadata used by frontend
    duration_minutes: Optional[int] = None
    rating: Optional[float] = None
    description: Optional[str] = None

    def to_dict(self):
        return {
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "rating": self.rating,
            "description": self.description,
        }


class DayPlan(BaseModel):
    day: int
    spots: List[Spot]
    total_distance_km: float = 0.0


class Itinerary(BaseModel):
    city: str
    days: List[DayPlan]
