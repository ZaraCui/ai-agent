from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class TransportMode(str, Enum):
    WALK = "walk"
    TRANSIT = "transit"
    TAXI = "taxi"


class NearbyFood(BaseModel):
    """周围美食信息"""
    name: str
    category: str  # 餐厅、咖啡厅等
    distance: float  # 距离（米）
    rating: Optional[float] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class NearbyShop(BaseModel):
    """周围商铺信息"""
    name: str
    category: str  # 购物、超市等
    distance: float  # 距离（米）
    phone: Optional[str] = None
    address: Optional[str] = None


class Spot(BaseModel):
    name: str
    lat: float
    lon: float
    category: str  # indoor / outdoor / food / museum / temple / shopping
    # optional metadata used by frontend
    duration_minutes: Optional[int] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    city: Optional[str] = None
    
    # 新增：周围美食和商铺
    nearby_foods: Optional[List[Dict[str, Any]]] = None  # 周围美食列表
    nearby_shops: Optional[List[Dict[str, Any]]] = None  # 周围商铺列表

    def to_dict(self):
        return {
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "rating": self.rating,
            "description": self.description,
            "city": self.city,
            "nearby_foods": self.nearby_foods,
            "nearby_shops": self.nearby_shops,
class DayPlan(BaseModel):
    day: int
    spots: List[Spot]
    total_distance_km: float = 0.0


class Itinerary(BaseModel):
    city: str
    days: List[DayPlan]
