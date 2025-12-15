import json
import os
import folium

from datetime import date
from agent.types import Spot
from agent.planner import plan_itinerary_soft_constraints, finalize_itinerary_distances
from agent.constraints import ScoreConfig
from agent.geometry import TransportMode
from agent.explainer import explain_recommendation, weather_advice
from agent.weather import get_weather
from agent.reasoning import explain_weather_trigger
from agent.replanner import replan_single_day
from agent.llm import generate_recommendation_reasoning


MAX_FORECAST_DAYS = 10  # Conservative: skip exact forecast-triggered actions beyond this window

# -----------------------------
# User interaction
# -----------------------------

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


def choose_preference() -> str:
    print("\nTravel preference options:")
    print("  1. Minimize walking")
    print("  2. Minimize transit time")
    print("  3. Minimize taxi usage")

    while True:
        choice = input("Please select a preference by number: ").strip()
        if choice == "1":
            return "walk"
        if choice == "2":
            return "transit"
        if choice == "3":
            return "taxi"
        print("Invalid selection, try again.")


def choose_start_date() -> date:
    print("\nEnter your trip start date (YYYY-MM-DD).")
    print("Press Enter to use today.")

    user_input = input("Start date: ").strip()
    if not user_input:
        return date.today()

    try:
        return date.fromisoformat(user_input)
    except ValueError:
        print("Invalid date format. Using today instead.")
        return date.today()


# -----------------------------
# Visualization
# -----------------------------

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
            folium.PolyLine(
                coords,
                color=colors[i % len(colors)],
            ).add_to(m)

    m.save(filepath)


# -----------------------------
# Main entry
# -----------------------------

def main() -> None:
    # --- Human input ---
    city = choose_city()
    print(f"\nPlanning itinerary for city: {city}")

    preference = choose_preference()
    print(f"Selected travel preference: {preference}\n")

    start_date = choose_start_date()
    print(f"Trip starts on: {start_date}")

    # --- Load data ---
    def load_spots(city_name: str) -> list[Spot]:
        path = f"data/spots_{city_name}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(f"No spot data found for city: {city_name}")
        return [Spot(**s) for s in json.load(open(path, encoding="utf-8"))]

    spots = load_spots(city)

    # --- Scoring configuration ---
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

    # --- Preference → mode mapping ---
    preference_to_mode = {
        "walk": TransportMode.WALK,
        "transit": TransportMode.TRANSIT,
        "taxi": TransportMode.TAXI,
    }
    preferred_mode = preference_to_mode[preference]

    # --- Run agent for all modes ---
    results = []

    for mode in TransportMode:
        itinerary, score, reasons = plan_itinerary_soft_constraints(
            city=city,
            spots=spots,
            days=3,
            cfg=cfg,
            mode=mode,
            trials=200,
        )

        out_path = f"output/{city}_map_{mode.value}.html"
        render_map(spots, itinerary, out_path)
        results.append((mode, itinerary, score, reasons, out_path))

    # --- Compare ---
    results.sort(key=lambda x: x[2])

    print("\n=== Mode Comparison (lower score is better) ===")
    for mode, _, score, reasons, out_path in results:
        tag = " (preferred)" if mode == preferred_mode else ""
        print(f"\nMode: {mode.value}{tag}")
        print(f"Score: {score:.2f}")
        print(f"Map:   {out_path}")
        if reasons:
            print("Self-check:")
            for r in reasons:
                print(" -", r)
        else:
            print("Self-check: no penalties")

    # --- Recommendation ---
    recommended = next((r for r in results if r[0] == preferred_mode), results[0])
    best_mode, best_itinerary, best_score, best_reasons, best_path = recommended

    # --- Final recommendation reasoning using LLM ---
    print("\n=== LLM Recommendation Explanation ===")
    llm_explanation = generate_recommendation_reasoning(best_itinerary, preference)
    print(llm_explanation)

    # Ensure distances are correct for explanation output
    finalize_itinerary_distances(best_itinerary)

    print("\n=== Recommendation ===")
    print(f"City: {city}")
    print(f"Recommended mode: {best_mode.value}")
    print(f"Reason: matches your preference ({preference})")
    print(f"Score: {best_score:.2f}")
    print(f"Map: {best_path}")
    if best_reasons:
        print("Notes:")
        for r in best_reasons:
            print(" -", r)

    print("\n=== Agent Explanation ===")
    print(
        explain_recommendation(
            itinerary=best_itinerary,
            mode=best_mode,
            score=best_score,
            reasons=best_reasons,
        )
    )

    print("\n=== Weather-based Suggestions ===")
    print(weather_advice(best_itinerary, start_date))

    # -----------------------------
    # Weather-triggered replanning
    # -----------------------------
    print("\n=== Weather-triggered Replanning ===")

    today = date.today()
    days_until_trip = (start_date - today).days

    if days_until_trip > MAX_FORECAST_DAYS:
        print(
            "⚠️ Weather-triggered replanning skipped: "
            "trip date is beyond reliable forecast range."
        )
        return

    replanned = False

    # Trigger replanning per-day if heavy rain expected
    for day in best_itinerary.days:
        if not day.spots:
            continue

        lat = day.spots[0].lat
        lon = day.spots[0].lon
        precipitation = get_weather(lat, lon)

        idx = day.day - 1
        if idx >= len(precipitation):
            continue

        rain_mm = precipitation[idx]

        if rain_mm >= 5.0:
            print(explain_weather_trigger(day.day, rain_mm))
            replan_single_day(best_itinerary, day.day - 1)
            replanned = True

    if replanned:
        # Refresh distances once after all repairs
        finalize_itinerary_distances(best_itinerary)

        print("\n=== Updated Itinerary After Replanning ===")
        for day in best_itinerary.days:
            if not day.spots:
                continue
            route = " → ".join(s.name for s in day.spots)
            print(f"Day {day.day}: {route}")
            print(f"  Estimated travel distance: {day.total_distance_km:.1f} km")
    else:
        print("No replanning needed: no heavy-rain days detected in forecast window.")


if __name__ == "__main__":
    main()
