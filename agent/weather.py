import requests
from typing import List

def get_daily_precipitation(lat: float, lon: float) -> List[float]:
    """
    Returns daily precipitation (mm) for the next days.
    Index 0 = today, 1 = tomorrow, etc.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=precipitation_sum"
        "&timezone=auto"
    )
    data = requests.get(url, timeout=10).json()
    return data["daily"]["precipitation_sum"]
