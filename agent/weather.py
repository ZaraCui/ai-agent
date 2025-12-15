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
