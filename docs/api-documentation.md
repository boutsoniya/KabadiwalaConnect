# API Reference

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/users` | Create citizen/collector/recycler |
| GET | `/api/users?role=collector` | List users by role |
| POST | `/api/pickups` | Create pickup request |
| GET | `/api/pickups` | List pickup requests |
| PATCH | `/api/pickups/{id}/assign/{collector_id}` | Assign collector |
| PATCH | `/api/pickups/{id}/status?status=picked_up` | Change pickup status |
| POST | `/api/quotes` | Calculate material value |

Interactive OpenAPI docs are available at `/docs` when the backend is running.