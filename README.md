# Travel Planning Agent
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
│   ├── weather.py        # Weather check
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
pip install folium openai
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

## 🌐 Deploying as a Web Application

### Local Development
Requirements
```python
Python 3.9+
```
Install dependencies:
```python
pip install -r requirements.txt
```

Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Run the web application:
```python
python app.py
```
Visit `http://localhost:5000` in your browser.

### Cloud Deployment

#### Option 1: Heroku (Recommended for beginners)
1. Create a Heroku account at https://heroku.com
2. Install Heroku CLI
3. Login and create an app:
```bash
heroku login
heroku create your-app-name
```
4. Set environment variables:
```bash
heroku config:set OPENAI_API_KEY=your_openai_api_key_here
```
5. Deploy:
```bash
git push heroku main
```
6. Open your app:
```bash
heroku open
```

#### Option 2: Railway
1. Go to https://railway.app and create an account
2. Connect your GitHub repository
3. Add environment variables in the Railway dashboard
4. Deploy automatically

#### Option 3: DigitalOcean App Platform
1. Create a DigitalOcean account
2. Use the App Platform service
3. Connect your repository and configure environment variables
4. Deploy

#### Option 4: AWS Elastic Beanstalk
1. Install AWS CLI and configure credentials
2. Create an EB application:
```bash
eb init -p python-3.9 travel-planning-agent
eb create production-env
```
3. Set environment variables in AWS console
4. Deploy updates with `eb deploy`

## 📌 Disclaimer

This project is an experimental planning agent for learning and exploration purposes.
Distances and travel times are approximations.

## 📫 Author

Built as a hands-on exploration of agent architectures and planning systems.

## 📦 Deployment with Docker and Let's Encrypt (docker-compose)

1. Update `deploy/nginx.conf` replacing `your.domain.com` with your real domain.
2. Ensure DNS A/AAAA records for your domain point to the host running this compose stack.
3. Start the stack (nginx will start and expose ACME webroot):
```
  docker-compose up -d
```
4. Obtain certificates using the included `certbot` helper (one-shot):

  ### replace your.domain.com accordingly
  ```
  docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
    -d your.domain.com --email your-email@example.com --agree-tos --no-eff-email
```
  ### after successful run, reload nginx to pick up certs
  ```
  docker-compose exec nginx nginx -s reload
```
Notes:
- Certificates are stored in the `certs` volume mounted at `/etc/letsencrypt` in the nginx service.
- Renew certificates periodically (e.g., via a cron job on the host that runs the same `docker-compose run certbot ...` command).
- For automated renewals, you can extend the compose setup to run certbot renew and reload nginx on success.
