import requests

def get_weather(lat: float, lon: float):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=precipitation_sum"
        "&timezone=auto"
    )
    data = requests.get(url, timeout=10).json()
    return data["daily"]["precipitation_sum"]

def is_bad_weather_day(rain_mm: float, threshold: float = 5.0) -> bool:
    return rain_mm >= threshold
