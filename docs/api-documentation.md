# API Reference

Base URL: `http://127.0.0.1:8000`

## Core endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/users` | Register a citizen, collector, or recycler |
| GET | `/api/users?role=collector` | List users by role |
| POST | `/api/pickups` | Create a pickup request |
| GET | `/api/pickups` | List pickup requests |
| GET | `/api/pickups/{id}/matches` | Find verified nearby collectors |
| PATCH | `/api/pickups/{id}/assign/{collector_id}` | Assign a collector |
| PATCH | `/api/pickups/{id}/status?status=picked_up` | Change pickup status |
| POST | `/api/pickups/{id}/weigh` | Record verified weight and final value |
| GET | `/api/transactions` | List payment/transaction records |
| POST | `/api/pickups/{id}/handoffs` | Record recycler handoff |
| GET | `/api/handoffs` | List recycler handoffs |
| POST | `/api/quotes` | Calculate material value |
| GET | `/api/impact` | Dashboard-ready impact metrics |

## Supported materials

`paper`, `plastic`, `cardboard`, `metal`, `glass`, `ewaste`

## Example: create a collector

```json
{
  "name": "Demo Collector",
  "phone": "8888888888",
  "role": "collector",
  "lat": 26.59,
  "lon": 74.86,
  "service_radius_km": 10
}
```

## Example: create a pickup

```json
{
  "citizen_id": 1,
  "material": "plastic",
  "estimated_weight_kg": 5,
  "address": "Demo address",
  "lat": 26.59,
  "lon": 74.86
}
```

## Example: record weighing

`POST /api/pickups/1/weigh`

```json
{
  "actual_weight_kg": 4.8,
  "payment_method": "upi"
}
```

The server calculates the final value from the material rate and verified weight, then marks the pickup completed.

Interactive OpenAPI documentation is available at `/docs` when the backend is running.
