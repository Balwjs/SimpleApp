# Trading Middleware (Dhan HQ)

A production-ready trading middleware bridging the Dhan HQ broker API with a unified real-time dashboard, automated Risk Management System (RMS), and a broker-level kill switch.

## Table of Contents
- Overview
- Architecture
- Features
  - Dashboard and UI (NiceGUI)
  - Positions and Margin
  - Orders and Order Book
  - Risk Management and Kill Switch
  - Market Data Test Proxy
- Installation & Requirements
  - Local (Windows/macOS/Linux)
  - Docker / Docker Compose
- Configuration (Environment Variables)
- Running
  - Local development
  - Production (Docker)
- Endpoints
- Database Models
- Logging & Monitoring
- Operational Notes
- Roadmap / Enhancements

## Overview
- Backend: FastAPI (ASGI), async/await throughout
- UI: NiceGUI (Python-based, no JavaScript required)
- Database: PostgreSQL in production, SQLite in development
- ORM: SQLModel (SQLAlchemy 2.x)
- HTTP Client: httpx (timeouts + retries)
- Scheduler: APScheduler (2-second risk polling)
- Caching/IPC: Redis (optional in dev, recommended in prod)
- Containerization: Docker + docker-compose
- Logging: structlog JSON; Prometheus metrics at `/metrics`

## Architecture
```
trading-middleware/
├── app/
│   ├── api/                 # FastAPI routers
│   ├── core/                # Config, logging, security
│   ├── db/                  # async engine/session
│   ├── models/              # SQLModel tables
│   ├── services/            # Dhan client, RMS, kill switch, scheduler, audit
│   └── ui/                  # NiceGUI pages (dashboard, positions, orders, risk)
├── docker/                  # Dockerfile
├── docker-compose.yml       # App + Postgres + Redis
├── requirements.txt
└── README.md
```

- `app/main.py`: Assembles the FastAPI app, includes routers, mounts NiceGUI, starts/stops scheduler via ASGI lifespan.
- `services/dhan_client.py`: Async client for Dhan v2 API with circuit breaker and retries.
- `services/scheduler.py`: 2-second polling job for risk logic.
- `services/risk_service.py`: Thresholds, lock mechanism, kill switch state + events.
- `services/kill_switch_executor.py`: Stubs to cancel orders, close positions, and block trading (extend with Dhan API calls).
- `services/audit_service.py`: Persist audit events.

## Features
### Dashboard and UI (NiceGUI)
- Mobile-friendly pages under `/` (dashboard), `/positions`, `/orders`, `/risk`.
- Real-time auto-refresh with timers; server push via Socket.IO under the hood.

### Positions and Margin
- `GET /api/positions` proxies to Dhan v2 `positions` and returns live positions.
- `GET /api/positions/margin` proxies to Dhan funds endpoint (if available on your plan).

### Orders and Order Book
- `GET /api/orders`: list orders from Dhan.
- `POST /api/orders`: place new orders (forward payload to Dhan as-is).
- `POST /api/orders/cancel_all`: cancel all open orders.

### Risk Management and Kill Switch
- 2-second global and per-position P&L checks (pluggable P&L calculation).
- Default thresholds (editable):
  - Max daily total loss: 1200 (close all)
  - Max daily loss per position: 200 (close position)
  - Per-position daily profit target: 500 (close position)
  - Max daily total profit target: 2200 (close all)
- Trigger actions at 95% of thresholds by design.
- Lock mechanism: "Lock Risk Settings for Day" prevents edits until 5 PM CT next trading day.
- Kill Switch (critical safety):
  - Auto activate on max loss/profit breach.
  - Manual activate/deactivate endpoints and UI controls.
  - Immediate actions: close all, cancel all, block new orders (extend via Dhan API).
  - Audit trail via `KillSwitchEvent` and `AuditLog`.

### Market Data Test Proxy
For quick testing against Dhan v2:
- `GET /api/market/proxy?path=<v2_path>&...`
- `POST /api/market/proxy?path=<v2_path>` (JSON body forwarded)
Use the exact `path` and payload from the Dhan swagger.

## Installation & Requirements
### Local (Windows/macOS/Linux)
- Python 3.11+
- Optional: PostgreSQL 16+, Redis 7+

```powershell
# Windows PowerShell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create .env
copy .env.example .env
# edit .env and set DHAN_BASE_URL + DHAN_API_KEY + SECRET (and DB/Redis if using)

# Run dev server (auto-reload)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Docker / Docker Compose
- Docker 24+
- Docker Compose v2

```bash
docker compose up --build -d
```

Containers:
- `trading_middleware_app`: gunicorn + uvicorn workers on port 8000
- `trading_middleware_db`: Postgres 16 (5432)
- `trading_middleware_redis`: Redis 7 (6379)

Healthchecks:
- App: GET `/api/healthz`
- DB: `pg_isready`

## Configuration (Environment Variables)
- `ENVIRONMENT` (development|production) – defaults to development locally, production in Docker
- `DATABASE_URL` – e.g. `sqlite+aiosqlite:///./app.db` (dev), `postgresql+asyncpg://app:app@db:5432/app`
- `REDIS_URL` – e.g. `redis://localhost:6379/0` or `redis://redis:6379/0`
- `SECRET` – JWT/crypto secret (set a strong random value for prod)
- `DHAN_BASE_URL` – `https://api.dhan.co/v2/` (prod) or `https://sandbox.dhan.co/v2/` (sandbox)
- `DHAN_API_KEY` – Dhan access token (sent as `access-token` header)
- `DHAN_CLIENT_ID` – optional reference

## Running
### Local Development
- UI: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/api/healthz`
- API Docs (OpenAPI): `http://127.0.0.1:8000/docs`
- Metrics (Prometheus): `http://127.0.0.1:8000/metrics`

### Production (Docker Compose)
- Ensure `.env` contains production values.
- `docker compose up --build -d`
- App is on host port `8000` by default.

## Endpoints
- System
  - `GET /api/healthz` – health
  - `GET /metrics` – Prometheus metrics
- Risk / Kill Switch
  - `GET /api/risk/settings`
  - `POST /api/risk/settings` – update thresholds (blocked when locked)
  - `POST /api/risk/lock` – lock until next trading day 5 PM CT
  - `POST /api/risk/unlock` – remove lock if expired
  - `GET /api/kill/status`
  - `POST /api/kill/activate` – body: `{ "reason": "..." }`
  - `POST /api/kill/deactivate` – body: `{ "reason": "..." }`
- Positions / Margin
  - `GET /api/positions`
  - `GET /api/positions/margin`
- Orders
  - `GET /api/orders`
  - `POST /api/orders` – forward to Dhan; pass raw body from swagger
  - `POST /api/orders/cancel_all`
- Market Test Proxy
  - `GET /api/market/proxy?path=<v2_path>&...`
  - `POST /api/market/proxy?path=<v2_path>` – body forwarded

## Database Models
- `RiskSettings` – user thresholds, lock flag, lock-until timestamp
- `KillSwitchStatus` – current status & reason
- `KillSwitchEvent` – activation/deactivation audit
- `AuditLog` – general audit trail (event, detail, path, success)

## Logging & Monitoring
- Logging: structlog JSON to stdout with timestamps and levels.
- Metrics: `prometheus_client` at `/metrics` for scraping by Prometheus/Grafana.

## Operational Notes
- Circuit breaker prevents repeatedly calling Dhan on persistent failures.
- Scheduler polls every 2 seconds (APScheduler) – adjust interval as needed.
- UI uses NiceGUI; in production, run with gunicorn (Dockerfile already does this).
- For TLS and reverse proxying, put Nginx or Caddy in front and forward to `app:8000`.

## Roadmap / Enhancements
- Replace the generic market proxy with typed LTP/Depth endpoints that match Dhan specs exactly.
- Implement live market WebSocket feed for real-time LTP/Depth.
- Master contract synchronization and fuzzy symbol search.
- Plug broker actions into `KillSwitchExecutor` to actually close/cancel at broker.
- Add authentication (fastapi-users with JWT) once dependency versions are aligned.

---

### Quick Commands
- Validate health:
```bash
curl -s http://127.0.0.1:8000/api/healthz
```
- Get positions:
```bash
curl -s http://127.0.0.1:8000/api/positions | jq .
```
- Test Dhan v2 path via proxy:
```bash
curl -s -X POST "http://127.0.0.1:8000/api/market/proxy?path=market/quotes/ltp" \
  -H "Content-Type: application/json" \
  -d '{"securities": {"NSE": ["<security_id_or_symbol>"]}}'
```

### Ports Used
- App: 8000/tcp
- Postgres (docker): 5432/tcp
- Redis (docker): 6379/tcp
