# Kabadiwala Connect ♻️

A digital bridge between households, informal waste collectors (kabadiwalas), aggregators, and formal recyclers.

## 🚀 Live Deployment

- **Live Demo:** https://kabadiwala-connect-djlz.onrender.com
- **Swagger API Docs:** https://kabadiwala-connect-api.onrender.com/docs
- **Health Check:** https://kabadiwala-connect-api.onrender.com/health
- **GitHub:** https://github.com/boutsoniya/KabadiwalaConnect

> The Render deployment is connected to the `main` branch, so future pushes automatically trigger a new deployment.

## Problem
Informal collectors are a critical part of India's recycling ecosystem, but collection requests, pricing, verification, weighing, payments, and downstream traceability are often fragmented.

## MVP
- Citizen registration and pickup requests
- Collector onboarding and verification workflow
- Location-aware pickup assignment
- Waste/material categorisation
- Estimated value calculation
- Pickup status tracking
- Weight and transaction records
- Recycler/aggregator handoff records
- Dashboards and basic analytics
- REST API with SQLite/PostgreSQL-ready persistence

## Architecture
```text
Citizen Web App ──┐
                  ├── FastAPI ── PostgreSQL
Collector App ────┤       │
Recycler Portal ──┘       ├── Pricing / Matching services
                          └── Notifications / audit trail
```

## Quick start

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger API documentation.

### Frontend
Open `frontend/index.html` with a local static server, or use any frontend dev server. The deployed frontend JavaScript is configured to use the live Render API by default.

## API endpoints
- `GET /health` — service health
- `POST /api/auth/register` — register a user
- `POST /api/auth/login` — authenticate a user
- `POST /api/users` — create a user
- `GET /api/users` — list users
- `POST /api/pickups` — create a pickup request
- `GET /api/pickups` — list pickup requests
- `GET /api/pickups/{id}/matches` — find nearby verified collectors
- `PATCH /api/pickups/{id}/assign/{collector_id}` — assign collector
- `PATCH /api/pickups/{id}/status` — update pickup status
- `POST /api/pickups/{id}/weigh` — record verified weight and transaction
- `GET /api/transactions` — list transactions
- `POST /api/pickups/{id}/handoffs` — record recycler handoff
- `GET /api/handoffs` — list recycler handoffs
- `POST /api/quotes` — calculate material value estimate
- `GET /api/impact` — view recycling impact metrics

## Project structure
```text
backend/       FastAPI application
frontend/      Responsive MVP web interface
database/      SQL schema and seed data
docs/          Architecture, API, database and deployment notes
scripts/       Developer utilities
tests/         API tests
.github/       CI workflow
```

## Environment
Copy `.env.example` to `.env` and change values for local deployment. Never commit real secrets.

## SIH
**Problem Statement:** SIH26229 — Kabadiwala Connect – Bringing the Informal Collector into the Formal Recycling Chain  
**Ministry:** Ministry of Mines  
**Theme:** Clean & Green Technology

## License
MIT
