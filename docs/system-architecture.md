# System Architecture

## Actors
- Citizen/household: creates pickup requests and receives status/value information.
- Informal collector (kabadiwala): accepts nearby jobs, records pickup and weight, and tracks earnings.
- Recycler/aggregator: receives sorted material and records downstream movement.
- Admin: verifies collectors, manages prices, resolves disputes and monitors analytics.

## Core flow
1. Citizen creates a pickup request.
2. Matching service finds eligible collectors using service area/distance and availability.
3. Collector accepts the request and updates status.
4. Material is weighed and categorised at pickup.
5. Pricing service calculates amount from material rate × verified weight.
6. Transaction is recorded with audit metadata.
7. Material is handed to an aggregator/recycler and the chain-of-custody event is recorded.

## Production components
Frontend (PWA/mobile) → API gateway → FastAPI services → PostgreSQL/Redis → notification provider.

Add authentication, rate limiting, role-based access, encrypted secrets, audit logging, object storage for optional evidence, and observability before production deployment.