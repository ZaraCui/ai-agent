# 🧠 Travel Planning Agent

A planning-based AI agent that automatically generates and optimizes multi-day travel itineraries under soft constraints such as travel time, daily workload, and transportation mode.

This project focuses on **agent-style decision making** rather than simple route generation:
the agent explores multiple candidate itineraries, evaluates them under different policies, and selects the best plan with interpretable reasons.

---

## ✨ Key Features

- **World Modeling**
  - Structured representation of cities, spots, daily plans, and itineraries
- **Planning & Search**
  - Initial itinerary construction
  - Local search with move / swap operators
- **Soft Constraint Optimization**
  - Daily travel time limits
  - Experience quality penalties (e.g. too few spots in a day)
  - Interpretable scoring and self-check reports
- **Policy-Conditioned Planning**
  - Supports multiple transportation modes:
    - 🚶 WALK
    - 🚇 TRANSIT
    - 🚕 TAXI
  - Same planner, different world rules
- **Visualization**
  - Interactive map output using Folium
  - Day-by-day routes and markers

---

## 🧩 System Architecture

```text
User Choice (Transport Mode)
        ↓
Planner (Search + Local Edits)
        ↓
Soft Constraints Scorer
        ↓
World Geometry (Time / Distance)
        ↓
Best Itinerary + Explanation


```

## 📁 Project Structure
```text
ai-agent/
├── agent/
│   ├── types.py          # Spot, DayPlan, Itinerary data models
│   ├── geometry.py       # Distance & travel-time rules
│   ├── planner.py        # Planning + local search logic
│   └── constraints.py   # Soft constraint scoring
│
├── data/
│   └── spots_tokyo.json  # Example spot dataset
│
├── output/
│   └── map.html          # Generated itinerary visualization
│
├── main.py               # Entry point
└── README.md
```

## 🚀 How It Works

Build Initial Plan

Spatially sort spots

Distribute them across days

Order each day using nearest-neighbor heuristics

Local Search Optimization

Randomly move or swap spots between days

Reorder affected days

Explore alternative itineraries

Soft Constraint Scoring

Total travel time (minutes)

Penalties for exceeding daily limits

Penalties for poor experience balance

Policy Conditioning

Evaluate the same itinerary under different transport modes

Select the best plan given the chosen policy

Visualization

Render final itinerary as an interactive map

## ▶️ Running the Project
Requirements
```python
Python 3.9+
folium
```
Install dependencies:
```python
pip install folium
```
Run
```python
python main.py
```

This will:

Generate an optimized itinerary

Print a self-check report

Save an interactive map to output/map.html

## 🔧 Example Configuration
```python
from agent.geometry import TransportMode
from agent.constraints import ScoreConfig

mode = TransportMode.WALK

cfg = ScoreConfig(
    max_daily_minutes={
        TransportMode.WALK: 240,
        TransportMode.TRANSIT: 300,
        TransportMode.TAXI: 360,
    },
    exceed_minute_penalty=1.5,
    one_spot_day_penalty=15.0,
)
```

## 🧠 Design Philosophy

Agent-first, not API-first

Explicit world rules instead of implicit LLM reasoning

Search + evaluation over one-shot generation

Human-controllable policies with interpretable outcomes

This project is intentionally designed to be extended into:

Multi-policy comparison agents

Human-in-the-loop itinerary selection

Real-world API integration (weather, routing, cost)

## 🌱 Future Extensions

Generate and compare itineraries for all transport modes

Add weather-aware planning

Cost-aware taxi constraints

Replace heuristic distance with real routing APIs

Multi-objective optimization (time × cost × comfort)

## 📌 Disclaimer

This project is an experimental planning agent for learning and exploration purposes.
Distances and travel times are approximations.

## 📫 Author

Built as a hands-on exploration of agent architectures and planning systems.