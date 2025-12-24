# Deploying the Flask Backend (Travel-Planning-Agent)

This document explains how to deploy the Flask backend (the API + server-side template renderer) and configure the frontend (if hosted separately) to call the remote backend safely.

## Overview
You have two recommended deployment patterns:

A. Deploy the full Flask app (serves the UI and API) — simplest and most secure for keeping `GOOGLE_MAPS_API_KEY` server-side.
B. Deploy Flask as an API backend (serves `/plan_itinerary` and `/api/directions`) and host frontend as static site (Vercel). In this case set `static/config.js` => `API_BASE` to the backend URL during build.

Below are step-by-step instructions for deploying to Render (example), with notes for Heroku and Cloud Run.

---

## Prerequisites
- A Google Cloud project with billing enabled.
- Enable the following Google APIs in Google Cloud Console (APIs & Services → Library):
  - Maps JavaScript API (if serving UI from backend)
  - Directions API (for route geometry)
- Create an API key in Google Cloud Console (APIs & Services → Credentials).
  - Add HTTP referrer restrictions for production (e.g. yourdomain.com/*).
  - For local testing include `http://localhost:5000/*`.

## Environment variables
Set the following environment variables on your host (Render/Heroku/Cloud Run):
- `GOOGLE_MAPS_API_KEY` = your Google Maps JS / Directions API key
- `PORT` (optional) = the port to listen on (default 5000)
- `FLASK_DEBUG` (optional) = `True` or `False`
- `CORS_ORIGINS` (optional) = comma-separated list of allowed origins for CORS (frontend). Example: `https://your-frontend.vercel.app`

---

## Deploy to Render (recommended simple PaaS)
1. Create a new Web Service in Render.
2. Connect your GitHub repo and choose the `main` branch.
3. Build & Start Command:
   - `pip install -r requirements.txt && gunicorn app:app`
4. Set Environment variables in the Render dashboard (see list above).
5. Deploy and wait for service to become healthy.

If you want Render to serve the frontend as well, the Flask app already renders `templates/index.html` and will inject `GOOGLE_MAPS_API_KEY` into the page.

---

## Deploy to Heroku (alternative)
1. Create a Heroku app and connect GitHub repo or push via `git push heroku main`.
2. Add Heroku Env Vars:
   - `heroku config:set GOOGLE_MAPS_API_KEY=your_key`
3. Use `Procfile` (already present in repo) and ensure requirements are installed.

---

## Deploy to Cloud Run (containerized)
1. Build a container image (e.g. Cloud Build or local Docker) that runs `gunicorn app:app`.
2. Push the image to Container Registry / Artifact Registry and deploy to Cloud Run.
3. Configure environment variables in Cloud Run service settings.

---

## If frontend is deployed separately (Vercel)
- Option 1 (recommended for more security): Host the frontend on the same backend service (serve `index.html` from Flask) so the backend injects `GOOGLE_MAPS_API_KEY` into the template at render-time.
- Option 2 (static frontend + remote backend): Add `GOOGLE_MAPS_API_KEY` to Vercel environment variables and during Vercel build generate `static/config.js` that contains the key and `API_BASE`. Example build command (Vercel project settings → Build Command):

```bash
# Inject API_BASE and GOOGLE_MAPS_API_KEY into static/config.js at build time
mkdir -p static
cat > static/config.js <<'JS'
const API_BASE='${API_BASE:-https://travel-planning-agent.onrender.com}';
const GOOGLE_MAPS_API_KEY='${GOOGLE_MAPS_API_KEY}';
JS
# then continue your normal build (if any)
```

Note: Even if you inject `GOOGLE_MAPS_API_KEY` at build-time into static assets, restrict the API key with HTTP referrers and keep it limited to the frontend domain.

---

## CORS
If your frontend is on a different origin, ensure `CORS_ORIGINS` environment variable on the backend includes your frontend origin (the Flask app reads `CORS_ORIGINS` to configure `Flask-Cors`).

Example:
```
CORS_ORIGINS=https://your-frontend.vercel.app
```

---

## Verifying the deployment
1. Visit the backend root URL. If you deployed the full app (Flask serves templates), the homepage should render and the Maps API key is injected.
2. If frontend is separate, ensure `static/config.js` has correct `API_BASE` and `GOOGLE_MAPS_API_KEY` values after build.
3. Open DevTools → Console and Network to verify:
   - No `ApiNotActivatedMapError` (means Maps JS API is enabled in GCP)
   - `/plan_itinerary` and `/api/directions` requests return `200` from your backend

---

## Security notes
- Prefer server-side rendering (backend serves the UI) to avoid exposing keys in repository or static assets.
- Always restrict API keys by HTTP referrer or API restrictions in Google Cloud.
- Do not commit secrets to the repository.

---

If you'd like, I can:
- Add a simple Render `service.yaml` or Dockerfile to this repo; or
- Add a Vercel build script example to write `static/config.js` during build; or
- Prepare a short `deploy.sh` helper to automate deployment steps.

Tell me which (Render/Heroku/Cloud Run) you prefer and I will add the automated helper files.
