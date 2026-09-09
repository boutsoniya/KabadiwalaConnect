from datetime import datetime
from enum import Enum
from math import asin, cos, radians, sin, sqrt
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Kabadiwala Connect API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    phone: str = Field(min_length=7, max_length=20)
    role: Role
    lat: Optional[float] = None
    lon: Optional[float] = None
    service_radius_km: float = Field(default=10, ge=1, le=100)


class User(UserCreate):
    id: int
    verified: bool = False
    created_at: datetime


class PickupCreate(BaseModel):
    citizen_id: int
    material: str
    estimated_weight_kg: float = Field(gt=0, le=10000)
    address: str = Field(min_length=5, max_length=500)
    lat: Optional[float] = None
    lon: Optional[float] = None


class Pickup(PickupCreate):
    id: int
    collector_id: Optional[int] = None
    status: PickupStatus
    estimated_value: float
    actual_weight_kg: Optional[float] = None
    final_value: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class PriceQuoteRequest(BaseModel):
    material: str
    weight_kg: float = Field(gt=0)


class WeightRecord(BaseModel):
    actual_weight_kg: float = Field(gt=0, le=10000)
    payment_method: str = "cash"


class HandoffCreate(BaseModel):
    recycler_id: int
    quantity_kg: float = Field(gt=0)
    destination: str = Field(min_length=2, max_length=200)
    notes: Optional[str] = None


users: dict[int, dict] = {}
pickups: dict[int, dict] = {}
transactions: dict[int, dict] = {}
handoffs: dict[int, dict] = {}
next_user_id = 1
next_pickup_id = 1
next_transaction_id = 1
next_handoff_id = 1

PRICES = {
    "paper": 12.0,
    "plastic": 20.0,
    "cardboard": 10.0,
    "metal": 35.0,
    "glass": 8.0,
    "ewaste": 70.0,
}


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance using the Haversine formula."""
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(a))


@app.get("/")
def root():
    return {"name": "Kabadiwala Connect API", "version": app.version}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/users", response_model=User)
def create_user(payload: UserCreate):
    global next_user_id
    if any(u["phone"] == payload.phone for u in users.values()):
        raise HTTPException(status_code=409, detail="Phone number already registered")
    user = {
        "id": next_user_id,
        **payload.model_dump(),
        "verified": payload.role == Role.citizen,
        "created_at": datetime.utcnow(),
    }
    users[next_user_id] = user
    next_user_id += 1
    return user


@app.get("/api/users", response_model=list[User])
def list_users(role: Optional[Role] = None):
    return [u for u in users.values() if role is None or u["role"] == role]


@app.post("/api/pickups", response_model=Pickup)
def create_pickup(payload: PickupCreate):
    global next_pickup_id
    if payload.citizen_id not in users or users[payload.citizen_id]["role"] != Role.citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    material = payload.material.lower().strip()
    if material not in PRICES:
        raise HTTPException(status_code=400, detail=f"Unsupported material: {material}")
    pickup = {
        "id": next_pickup_id,
        **payload.model_dump(),
        "material": material,
        "collector_id": None,
        "status": PickupStatus.requested,
        "estimated_value": round(payload.estimated_weight_kg * PRICES[material], 2),
        "actual_weight_kg": None,
        "final_value": None,
        "created_at": datetime.utcnow(),
        "completed_at": None,
    }
    pickups[next_pickup_id] = pickup
    next_pickup_id += 1
    return pickup


@app.get("/api/pickups", response_model=list[Pickup])
def list_pickups(status: Optional[PickupStatus] = None):
    return [p for p in pickups.values() if status is None or p["status"] == status]


@app.patch("/api/pickups/{pickup_id}/assign/{collector_id}", response_model=Pickup)
def assign_collector(pickup_id: int, collector_id: int):
    if pickup_id not in pickups:
        raise HTTPException(status_code=404, detail="Pickup not found")
    if collector_id not in users or users[collector_id]["role"] != Role.collector:
        raise HTTPException(status_code=404, detail="Collector not found")
    collector = users[collector_id]
    if not collector["verified"]:
        raise HTTPException(status_code=403, detail="Collector is not verified")
    pickup = pickups[pickup_id]
    pickup["collector_id"] = collector_id
    pickup["status"] = PickupStatus.assigned
    return pickup


@app.get("/api/pickups/{pickup_id}/matches")
def match_collectors(pickup_id: int, limit: int = 5):
    if pickup_id not in pickups:
        raise HTTPException(status_code=404, detail="Pickup not found")
    pickup = pickups[pickup_id]
    if pickup["lat"] is None or pickup["lon"] is None:
        return {"matches": [], "message": "Pickup coordinates are required for location matching"}
    matches = []
    for collector in users.values():
        if collector["role"] != Role.collector or not collector["verified"]:
            continue
        if collector["lat"] is None or collector["lon"] is None:
            continue
        distance = distance_km(pickup["lat"], pickup["lon"], collector["lat"], collector["lon"])
        if distance <= collector["service_radius_km"]:
            matches.append({"collector": collector, "distance_km": round(distance, 2)})
    matches.sort(key=lambda item: item["distance_km"])
    return {"matches": matches[: max(1, min(limit, 20))]}


@app.patch("/api/pickups/{pickup_id}/status", response_model=Pickup)
def update_pickup_status(pickup_id: int, status: PickupStatus):
    if pickup_id not in pickups:
        raise HTTPException(status_code=404, detail="Pickup not found")
    pickup = pickups[pickup_id]
    pickup["status"] = status
    if status == PickupStatus.completed:
        pickup["completed_at"] = datetime.utcnow()
    return pickup


@app.post("/api/pickups/{pickup_id}/weigh", response_model=Pickup)
def record_weight(pickup_id: int, payload: WeightRecord):
    global next_transaction_id
    if pickup_id not in pickups:
        raise HTTPException(status_code=404, detail="Pickup not found")
    pickup = pickups[pickup_id]
    rate = PRICES[pickup["material"]]
    amount = round(payload.actual_weight_kg * rate, 2)
    pickup["actual_weight_kg"] = payload.actual_weight_kg
    pickup["final_value"] = amount
    transactions[next_transaction_id] = {
        "id": next_transaction_id,
        "pickup_id": pickup_id,
        "weight_kg": payload.actual_weight_kg,
        "rate_per_kg": rate,
        "amount_inr": amount,
        "payment_method": payload.payment_method,
        "status": "recorded",
        "recorded_at": datetime.utcnow(),
    }
    next_transaction_id += 1
    pickup["status"] = PickupStatus.completed
    pickup["completed_at"] = datetime.utcnow()
    return pickup


@app.get("/api/transactions")
def list_transactions():
    return list(transactions.values())


@app.post("/api/pickups/{pickup_id}/handoffs")
def create_handoff(pickup_id: int, payload: HandoffCreate):
    global next_handoff_id
    if pickup_id not in pickups:
        raise HTTPException(status_code=404, detail="Pickup not found")
    if payload.recycler_id not in users or users[payload.recycler_id]["role"] != Role.recycler:
        raise HTTPException(status_code=404, detail="Recycler not found")
    handoff = {
        "id": next_handoff_id,
        "pickup_id": pickup_id,
        **payload.model_dump(),
        "recorded_at": datetime.utcnow(),
    }
    handoffs[next_handoff_id] = handoff
    next_handoff_id += 1
    return handoff


@app.get("/api/handoffs")
def list_handoffs():
    return list(handoffs.values())


@app.post("/api/quotes")
def quote(payload: PriceQuoteRequest):
    material = payload.material.lower().strip()
    if material not in PRICES:
        raise HTTPException(status_code=400, detail=f"Unsupported material: {material}")
    rate = PRICES[material]
    return {"material": material, "rate_per_kg": rate, "weight_kg": payload.weight_kg, "estimated_value": round(rate * payload.weight_kg, 2)}


@app.get("/api/impact")
def impact_metrics():
    completed = [p for p in pickups.values() if p["status"] == PickupStatus.completed]
    total_kg = sum((p["actual_weight_kg"] or 0) for p in completed)
    total_value = sum((p["final_value"] or 0) for p in completed)
    by_material: dict[str, float] = {}
    for p in completed:
        by_material[p["material"]] = round(by_material.get(p["material"], 0) + (p["actual_weight_kg"] or 0), 2)
    return {
        "total_pickups": len(pickups),
        "completed_pickups": len(completed),
        "total_recycled_kg": round(total_kg, 2),
        "total_value_inr": round(total_value, 2),
        "material_breakdown_kg": by_material,
        "registered_collectors": len([u for u in users.values() if u["role"] == Role.collector]),
        "registered_recyclers": len([u for u in users.values() if u["role"] == Role.recycler]),
    }
