import json
import os
import folium
import sys

from agent.types import Spot
from agent.planner import plan_itinerary_soft_constraints
from agent.constraints import ScoreConfig
from agent.geometry import TransportMode

def choose_city() -> str:
    available_cities = [
        f.replace("spots_", "").replace(".json", "")
        for f in os.listdir("data")
        if f.startswith("spots_")
    ]

    if not available_cities:
        raise RuntimeError("No city data found in data/")

    print("Available cities:")
    for i, city in enumerate(available_cities, start=1):
        print(f"  {i}. {city}")

    while True:
        choice = input("Please select a city by number: ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue

        idx = int(choice) - 1
        if 0 <= idx < len(available_cities):
            return available_cities[idx]

        print("Invalid selection, try again.")


CITY = choose_city()
print(f"\nPlanning itinerary for city: {CITY}\n")


def render_map(spots: list[Spot], itinerary, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    m = folium.Map(location=[spots[0].lat, spots[0].lon], zoom_start=12)
    colors = ["red", "blue", "green", "purple", "orange"]

    for i, day in enumerate(itinerary.days):
        coords = []
        for s in day.spots:
            folium.Marker(
                [s.lat, s.lon],
                popup=f"Day {day.day}: {s.name}",
            ).add_to(m)
            coords.append([s.lat, s.lon])

        if len(coords) >= 2:
            folium.PolyLine(coords, color=colors[i % len(colors)]).add_to(m)

    m.save(filepath)


def main() -> None:
    CITY = choose_city()
    print(f"\nPlanning itinerary for city: {CITY}\n")

    def load_spots(city: str) -> list[Spot]:
        path = f"data/spots_{city}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(f"No spot data found for city: {city}")
        return [
            Spot(**s)
            for s in json.load(open(path, encoding="utf-8"))
        ]

    spots = load_spots(CITY)

    cfg = ScoreConfig(
        max_daily_minutes={
            TransportMode.WALK: 240,
            TransportMode.TRANSIT: 300,
            TransportMode.TAXI: 360,
        },
        exceed_minute_penalty=1.5,
        one_spot_day_penalty=15.0,
        min_spots_per_day=2,
    )

    results = []

    for mode in TransportMode:
        itinerary, score, reasons = plan_itinerary_soft_constraints(
            city=CITY,
            spots=spots,
            days=3,
            cfg=cfg,
            mode=mode,
            trials=200,
        )

        out_path = f"output/{CITY}_map_{mode.value}.html"
        render_map(spots, itinerary, out_path)

        results.append((mode, itinerary, score, reasons, out_path))

    results.sort(key=lambda x: x[2])

    print("=== Mode Comparison (lower score is better) ===")
    for mode, _, score, reasons, out_path in results:
        print(f"\nMode: {mode.value}")
        print(f"Score: {score:.2f}")
        print(f"Map:   {out_path}")
        if reasons:
            print("Self-check:")
            for r in reasons:
                print(" -", r)
        else:
            print("Self-check: no penalties")

    best_mode, _, best_score, best_reasons, best_path = results[0]
    print("\n=== Recommendation ===")
    print(f"Best mode: {best_mode.value}")
    print(f"Best score: {best_score:.2f}")
    print(f"Map: {best_path}")


if __name__ == "__main__":
    main()
