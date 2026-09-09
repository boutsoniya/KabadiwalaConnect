from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Kabadiwala Connect API", version="0.1.0", description="MVP API for connecting citizens, informal collectors and recyclers.")

class Role(str, Enum):
    citizen = "citizen"
    collector = "collector"
    recycler = "recycler"

class PickupStatus(str, Enum):
    requested = "requested"
    assigned = "assigned"
    picked_up = "picked_up"
    completed = "completed"
    cancelled = "cancelled"

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=8, max_length=20)
    role: Role
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class User(UserCreate):
    id: int
    verified: bool = False

class PickupCreate(BaseModel):
    citizen_id: int
    material: str = Field(min_length=2, max_length=50)
    estimated_weight_kg: float = Field(gt=0)
    address: str = Field(min_length=5, max_length=300)

class Pickup(PickupCreate):
    id: int
    status: PickupStatus = PickupStatus.requested
    collector_id: Optional[int] = None
    created_at: datetime

class PriceQuoteRequest(BaseModel):
    material: str
    weight_kg: float = Field(gt=0)

users: dict[int, User] = {}
pickups: dict[int, Pickup] = {}
next_user_id = 1
next_pickup_id = 1

# Demo pricing table; replace with admin-managed market prices in production.
PRICE_PER_KG = {"paper": 12.0, "plastic": 20.0, "cardboard": 10.0, "metal": 35.0, "glass": 8.0, "ewaste": 70.0}

@app.get("/", tags=["health"])
def root():
    return {"service": "Kabadiwala Connect API", "status": "ok", "version": "0.1.0"}

@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}

@app.post("/api/users", response_model=User, tags=["users"])
def create_user(payload: UserCreate):
    global next_user_id
    user = User(id=next_user_id, **payload.model_dump())
    users[user.id] = user
    next_user_id += 1
    return user

@app.get("/api/users", response_model=list[User], tags=["users"])
def list_users(role: Optional[Role] = None):
    values = list(users.values())
    return [u for u in values if role is None or u.role == role]

@app.post("/api/pickups", response_model=Pickup, tags=["pickups"])
def create_pickup(payload: PickupCreate):
    global next_pickup_id
    if payload.citizen_id not in users or users[payload.citizen_id].role != Role.citizen:
        raise HTTPException(400, "citizen_id must belong to a citizen user")
    pickup = Pickup(id=next_pickup_id, created_at=datetime.utcnow(), **payload.model_dump())
    pickups[pickup.id] = pickup
    next_pickup_id += 1
    return pickup

@app.get("/api/pickups", response_model=list[Pickup], tags=["pickups"])
def list_pickups(status: Optional[PickupStatus] = None):
    values = list(pickups.values())
    return [p for p in values if status is None or p.status == status]

@app.patch("/api/pickups/{pickup_id}/assign/{collector_id}", response_model=Pickup, tags=["pickups"])
def assign_pickup(pickup_id: int, collector_id: int):
    if pickup_id not in pickups:
        raise HTTPException(404, "Pickup not found")
    if collector_id not in users or users[collector_id].role != Role.collector:
        raise HTTPException(400, "collector_id must belong to a collector")
    pickup = pickups[pickup_id]
    pickup.collector_id = collector_id
    pickup.status = PickupStatus.assigned
    return pickup

@app.patch("/api/pickups/{pickup_id}/status", response_model=Pickup, tags=["pickups"])
def update_status(pickup_id: int, status: PickupStatus):
    if pickup_id not in pickups:
        raise HTTPException(404, "Pickup not found")
    pickups[pickup_id].status = status
    return pickups[pickup_id]

@app.post("/api/quotes", tags=["pricing"])
def quote(payload: PriceQuoteRequest):
    key = payload.material.strip().lower()
    rate = PRICE_PER_KG.get(key)
    if rate is None:
        raise HTTPException(404, "No price configured for this material")
    return {"material": key, "weight_kg": payload.weight_kg, "rate_per_kg": rate, "estimated_value": round(rate * payload.weight_kg, 2), "currency": "INR"}
