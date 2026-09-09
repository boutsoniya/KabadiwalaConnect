# Kabadiwala Connect ♻️

A digital bridge between households, informal waste collectors (kabadiwalas), aggregators, and formal recyclers.

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
                  ├── FastAPI ── Database
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
Open `frontend/index.html` with a local static server, or use any frontend dev server. Set `API_BASE_URL` in `frontend/app.js` if the API is not on localhost:8000.

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