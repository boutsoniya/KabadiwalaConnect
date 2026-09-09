# Implementation Roadmap

## Phase 1 — MVP
- Citizen pickup request
- Collector onboarding and verification
- Material price estimation
- Pickup assignment and status tracking
- Weight and payment recording

## Phase 2 — Network
- Geo-based collector matching
- Collector availability and service radius
- Recycler/aggregator portal
- Digital receipts and transaction history
- Notifications

## Phase 3 — Trust & Analytics
- Collector verification badges
- Duplicate/fraud detection
- Audit trail for material handoffs
- Waste diversion and recycling impact metrics
- Admin pricing controls

## Phase 4 — Production
- PostgreSQL-backed persistence
- JWT authentication and role-based access control
- Object storage for optional pickup evidence
- Observability, backups and rate limiting
- Deployment with managed database and HTTPS

## Hackathon demo path
1. Register a citizen.
2. Request 5 kg of recyclable material.
3. Show the estimated INR value.
4. Assign a nearby collector.
5. Update pickup to picked_up/completed.
6. Record actual weight and payment.
7. Show the recycling-chain transaction and impact dashboard.
