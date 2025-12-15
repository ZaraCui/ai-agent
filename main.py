import json
import folium

from agent.types import Spot
from agent.planner import plan_itinerary_soft_constraints
from agent.constraints import ScoreConfig
from agent.geometry import TransportMode

mode = TransportMode.WALK  # Set transport mode for scoring

# Load data
spots = [
    Spot(**s)
    for s in json.load(open("data/spots_tokyo.json", encoding="utf-8"))
]

# Configure soft constraints
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

# Run agent planner (search + scoring)
itinerary, score, reasons = plan_itinerary_soft_constraints(
    city="Tokyo",
    spots=spots,
    days=3,
    cfg=cfg,
    mode=TransportMode.WALK,
    trials=200
)

# Print self-check report
print(f"Best score: {score:.2f}")

if reasons:
    print("Self-check report:")
    for r in reasons:
        print(" -", r)
else:
    print("Self-check report: no penalties")

# Visualize on map
m = folium.Map(location=[spots[0].lat, spots[0].lon], zoom_start=12)
colors = ["red", "blue", "green"]

for i, day in enumerate(itinerary.days):
    coords = []
    for s in day.spots:
        folium.Marker(
            [s.lat, s.lon],
            popup=f"Day {day.day}: {s.name}"
        ).add_to(m)
        coords.append([s.lat, s.lon])

    if len(coords) >= 2:
        folium.PolyLine(coords, color=colors[i % len(colors)]).add_to(m)

m.save("output/map.html")
print("Saved output/map.html")
