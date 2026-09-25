# Virsa — Community-Centric Intelligent Tourism Ecosystem

A full-stack demonstration for Smart India Hackathon (SIH) — a living "smart tourism" platform covering **5 destinations** (Vadodara, Ahmedabad, Kutch, Jaipur, Varanasi), with a public consumer app, an artisan/business portal, and an authority command centre, all running on live simulated sensor + crowd data with a festival-mode community feedback loop.

**Bilingual (English / हिन्दी)** throughout the UI, with per-destination content, audio narration, and text-to-speech on the page, hero and AI guide answers.

**Festival scenario:** Navratri 2026 (Oct 11–20). The marketplace collects resident reports + venue crowd telemetry; one live data loop drives every screen.

## What's inside

| Experience | Highlights |
|---|---|
| **Public app** | Interactive cultural map with live markers, story-mode place deep-dives with audio narration, artisans & handcrafts, cultural experiences, festival mode + events, stays with live occupancy, **Virsa Guide** (RAG-style AI assistant), resident issue reporting with click-to-pin map + AI triage, live recommendations pushed from authority approvals |
| **Business portal** | Register/manage artisan & stay businesses, product catalogue, visitor enquiries with reply workflow |
| **Authority command centre** | Live overview KPIs, heat-map of real-time crowd concentration, 30-day + hourly footfall analytics, capacity/crowd-risk assessment, alternative-venue recommendations (approval broadcasts to the public app), demand forecasting, events/notices/closures/parking management, resident-report workflow with officer notes, business verification, hotel occupancy |

**Seeded catalogue:** 5 destinations · 54 places · 43 businesses · 15 experiences · 5 festivals · 16 events · 60 days of footfall history.

**Destination switching** is global and instant — selecting a destination re-scopes the map, catalogue, dashboards, page title, and audio voice.

## Architecture

```
┌─────────────┐   HTTP/JSON    ┌──────────────────────────────┐
│  React SPA  │ ─────────────► │  FastAPI backend (uvicorn)   │
│ (Vite + TS) │ ◄───────────── │  - SQLAlchemy 2.0 + SQLite/  │
│  /api, /ws  │    WS channel  │    Postgres                  │
└─────────────┘                │  - live-tick simulator       │
                               │  - AI: forecast, crowd-risk, │
                               │    alternatives, assistant,  │
                               │    report classifier (sklearn)│
                               └──────────────────────────────┘
```

- **Live data loop**: a per-second simulator walks Navratri crowd telemetry (visitor flow, capacity, parking, alerts). The backend broadcasts to `public` / `authority` / `business` WebSocket channels, and the SPA polls `/api/map/info` so every screen refreshes in place.
- **AI services are modular** (`backend/app/services/`): LocalOutlier-Based crowding classifier, capacity-corrected footfall forecast, synthetic-vine alternative recommendations, catalog-grounded Virsa Guide, NB-heuristic report classifier (µ=0.0, σ=0.06). No hallucinated answers.

## Tech stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, PyJWT, passlib/bcrypt, scikit-learn, WebSockets
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, react-leaflet + OSM, recharts, react-router v6
- **Storage**: SQLite by default (zero-dependency prototype); Postgres 16 via `DATABASE_URL` in Docker

## Demo accounts

All passwords: **`demo1234`**

| Role | Email | Use |
|---|---|---|
| Public | `tourist@demo.com` | Browse the platform |
| Public | `resident@demo.com` | Report issues (AI triaged) |
| Artisan / Business | `artisan@demo.com` | Business portal |
| Authority (Admin) | `admin@demo.com` | Command centre full access |
| Authority (Officer) | `officer@demo.com` | Operations workflow |

Registration is open — public visitors can also register a tourist/resident/artisan account.

## Run it locally

Requires Python 3.12+ and Node 18+.

### Backend (port 8000)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

First boot seeds the full demo catalogue, then starts the live simulator. Run with Postgres:

```bash
DATABASE_URL=postgresql+psycopg://virsa:virsa@localhost:5432/virsa uvicorn app.main:app --port 8000
```

### Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev          # proxies /api and /ws → localhost:8000
```

Open http://localhost:5173 — log in with any demo account. Try: assistant → "where can we see garba tonight?", authority "Crowd" → assess → suggest alternatives → approve (public map shows it instantly), resident "Report" → click a spot on the map to pin.

## Deploy

### Option A — single VPS with Docker (recommended)

Needs a Linux host with Docker Engine + the Compose plugin. Copy the repo, then:

```bash
cd infra
cp .env.example .env        # then edit .env: set JWT_SECRET and a real Postgres password
docker compose up -d --build
docker compose ps
```

This brings up Postgres 16, the FastAPI backend on `:8000` and the nginx-served frontend on `:8080` (SPA build + `/api` and `/ws` reverse-proxy in one container). The database auto-seeds on first start.

Then put TLS in front of it. Any of these work:

```bash
# Caddy (simplest — automatic HTTPS, needs ports 80/443 open)
caddy run --config Caddyfile        # then: yourdomain.com { reverse_proxy localhost:8080 }
```

```nginx
# or nginx + certbot
server {
  server_name yourdomain.com;
  location / { proxy_pass http://127.0.0.1:8080; proxy_set_header Host $host; }
  location /ws/ { proxy_pass http://127.0.0.1:8080; proxy_http_version 1.1;
                  proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; }
}
sudo certbot --nginx -d yourdomain.com
```

Point the DNS `A` record at the server IP first.

### Option B — Render / Railway / Fly.io (managed)

1. **Postgres** — provision a managed Postgres, copy its connection string.
2. **Backend** — build from `backend/` (Dockerfile included), port `8000`, health path `/api/destinations`.
   Env: `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS=https://your-frontend-domain`, `SEED_ON_STARTUP=true`.
3. **Frontend** — build from `frontend/`, static output in `dist/`, publish directory `dist`, and
   route `/api` to the backend (see Option C for the exact rewrite).
4. Because this is a Vite SPA, add a **rewrite** rule sending all unmatched paths to `/index.html`, or deep links like `/authority` will 404 on refresh.

### Option C — frontend on Vercel/Netlify + backend anywhere

The frontend calls `/api` **relatively**, so the recommended setup is to proxy `/api` from the CDN to the backend. Requests then stay same-origin, the SPA fallback works, and CORS is never involved.

1. Deploy `frontend/` (Root Directory = `frontend`). `vercel.json` is included and already sets build command, `dist` output, the `/api/:path*` proxy and the SPA fallback — you only need to replace `YOUR-BACKEND-HOST`.
2. Replace the placeholder in `frontend/vercel.json`:

   ```json
   "destination": "https://api.your-domain.com/api/:path*"
   ```

3. Deploy the backend separately (Render/Railway/Fly) from `backend/`, port `8000`, and set `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, `SEED_ON_STARTUP=true`.

Only if your host cannot rewrite `/api`, set the build-time env var `VITE_API_TARGET=https://api.your-domain.com` instead — `api.ts` then calls the backend by absolute URL and the backend **must** list the frontend origin in `CORS_ORIGINS` (custom `X-Destination-Id` header triggers a preflight). It is baked in at build time, so changing it requires a redeploy.

<details>
<summary>Netlify equivalent (<code>frontend/netlify.toml</code>)</summary>

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/api/*"
  to = "https://api.your-domain.com/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

</details>

> The UI refreshes by polling every 20s, not by WebSocket, so no socket or `wss://` configuration is required on the CDN. The backend still exposes `/ws` for programmatic use.

### Before going live

- [ ] Replace `JWT_SECRET` with a long random value: `openssl rand -hex 32`
- [ ] Replace the Postgres password (currently the demo value `virsa`) — keep it URL-safe
- [ ] Set `CORS_ORIGINS` to your real frontend origin only
- [ ] Set `SEED_ON_STARTUP=false` once you have real data you don't want re-seeded
- [ ] `virsa.db` is gitignored — for real use set `DATABASE_URL` to Postgres so data survives rebuilds
- [ ] Serve over HTTPS (required for WebSockets and microphone/TTS in most browsers)
- [ ] Add a reverse proxy with a 3600s read timeout so `/ws` isn't cut off

## Run with Docker

```bash
cd infra
docker compose up --build        # postgres + backend :8000 + frontend :8080
```

Open http://localhost:8080 (frontend proxies `/api` and `/ws` to backend).

## API surface

Public: `GET /api/destinations`, `/places`, `/map/markers|emoji-markers`, `/map/info`, `/artisans`, `/experiences`, `/festivals`, `/events`, `/hotels`, `/hotels/aggregate`, `POST /api/assistant/ask`, `POST /api/enquiries`, `POST /api/reports`, plus auth. Authority (JWT): `/api/authority/overview|live-map|analytics|crowd-assessment|recommendations|forecast|events|alerts|closures|parking|reports|businesses|hotels/aggregate`. Full schema at `/api/openapi.json`.

## Layout

```
backend/app/            FastAPI app (api/, services/, seed/, core/)
frontend/src/           Vite React app
  pages/                public app (map, places, artisans, festivals, stays, assistant, reports…)
  authority/            command centre + AuthorityApp shell
  business/             business portal
infra/                  docker-compose
```

## Notes

- Runs in **demo mode** by default: all analytics/crowd data is simulated and labelled `is_demo` so it is never mistaken for real stats.
- Classic govt. site contrast rules kept in mind — heading/body contrast ≥ 4.5:1, focus states and semantic landmarks included, no auto-playing media.