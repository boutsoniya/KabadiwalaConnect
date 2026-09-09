from datetime import datetime
from enum import Enum
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import create_access_token, decode_access_token, hash_password, verify_password
from .database import Base, engine, get_db
from .models import Pickup as PickupModel, RecyclerHandoff, Transaction, User as UserModel

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Kabadiwala Connect API", version="0.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

PRICES = {"paper": 12.0, "plastic": 20.0, "cardboard": 10.0, "metal": 35.0, "glass": 8.0, "ewaste": 70.0}
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

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

class AuthRegister(UserCreate):
    password: str = Field(min_length=8, max_length=128)

class AuthLogin(BaseModel):
    phone: str
    password: str

class UserOut(UserCreate):
    id: int
    verified: bool
    created_at: datetime

class PickupCreate(BaseModel):
    citizen_id: int
    material: str
    estimated_weight_kg: float = Field(gt=0, le=10000)
    address: str = Field(min_length=5, max_length=500)
    lat: Optional[float] = None
    lon: Optional[float] = None

class PickupOut(PickupCreate):
    id: int
    collector_id: Optional[int]
    status: PickupStatus
    estimated_value: float
    actual_weight_kg: Optional[float]
    final_value: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]

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

def price_for(material: str) -> float:
    material = material.lower().strip()
    if material not in PRICES:
        raise HTTPException(status_code=400, detail=f"Unsupported material: {material}")
    return PRICES[material]

def user_out(u: UserModel) -> dict:
    return {"id": u.id, "name": u.name, "phone": u.phone, "role": u.role, "verified": u.verified, "lat": u.lat, "lon": u.lon, "service_radius_km": u.service_radius_km, "created_at": u.created_at}

def pickup_out(p: PickupModel) -> dict:
    return {"id": p.id, "citizen_id": p.citizen_id, "collector_id": p.collector_id, "material": p.material, "estimated_weight_kg": p.estimated_weight_kg, "actual_weight_kg": p.actual_weight_kg, "address": p.address, "lat": p.lat, "lon": p.lon, "status": p.status, "estimated_value": p.estimated_value, "final_value": p.final_value, "created_at": p.created_at, "completed_at": p.completed_at}

def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    a = sin(radians(lat2-lat1)/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(radians(lon2-lon1)/2)**2
    return 6371.0 * 2 * asin(sqrt(a))

def current_user(token: Optional[str], db: Session) -> Optional[UserModel]:
    if not token:
        return None
    try:
        data = decode_access_token(token)
        return db.get(UserModel, int(data["sub"]))
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_role(token: Optional[str], db: Session, roles: set[str]) -> UserModel:
    user = current_user(token, db)
    if not user or user.role not in roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user

@app.get("/", include_in_schema=False)
def root():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"name": "Kabadiwala Connect API", "version": app.version}

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}

@app.get("/app.js", include_in_schema=False)
def frontend_js():
    return FileResponse(FRONTEND_DIR / "app.js")

@app.get("/styles.css", include_in_schema=False)
def frontend_css():
    return FileResponse(FRONTEND_DIR / "styles.css")

@app.post("/api/auth/register")
def register(payload: AuthRegister, db: Session = Depends(get_db)):
    if db.scalar(select(UserModel).where(UserModel.phone == payload.phone)):
        raise HTTPException(status_code=409, detail="Phone number already registered")
    u = UserModel(name=payload.name, phone=payload.phone, role=payload.role.value, verified=payload.role == Role.citizen, lat=payload.lat, lon=payload.lon, service_radius_km=payload.service_radius_km, password_hash=hash_password(payload.password))
    db.add(u); db.commit(); db.refresh(u)
    return {"access_token": create_access_token(str(u.id), u.role), "token_type": "bearer", "user": user_out(u)}

@app.post("/api/auth/login")
def login(payload: AuthLogin, db: Session = Depends(get_db)):
    u = db.scalar(select(UserModel).where(UserModel.phone == payload.phone))
    if not u or not u.password_hash or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    return {"access_token": create_access_token(str(u.id), u.role), "token_type": "bearer", "user": user_out(u)}

@app.post("/api/users", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(UserModel).where(UserModel.phone == payload.phone)):
        raise HTTPException(status_code=409, detail="Phone number already registered")
    u = UserModel(**payload.model_dump(), role=payload.role.value, verified=payload.role == Role.citizen)
    db.add(u); db.commit(); db.refresh(u)
    return user_out(u)

@app.get("/api/users", response_model=list[UserOut])
def list_users(role: Optional[Role] = None, db: Session = Depends(get_db)):
    q = select(UserModel)
    if role: q = q.where(UserModel.role == role.value)
    return [user_out(u) for u in db.scalars(q).all()]

@app.post("/api/pickups", response_model=PickupOut)
def create_pickup(payload: PickupCreate, db: Session = Depends(get_db)):
    citizen = db.get(UserModel, payload.citizen_id)
    if not citizen or citizen.role != Role.citizen: raise HTTPException(status_code=404, detail="Citizen not found")
    material = payload.material.lower().strip(); rate = price_for(material)
    p = PickupModel(**payload.model_dump(), material=material, status=PickupStatus.requested.value, estimated_value=round(payload.estimated_weight_kg*rate, 2))
    db.add(p); db.commit(); db.refresh(p)
    return pickup_out(p)

@app.get("/api/pickups", response_model=list[PickupOut])
def list_pickups(status: Optional[PickupStatus] = None, db: Session = Depends(get_db)):
    q = select(PickupModel)
    if status: q = q.where(PickupModel.status == status.value)
    return [pickup_out(p) for p in db.scalars(q).all()]

@app.get("/api/pickups/{pickup_id}/matches")
def match_collectors(pickup_id: int, limit: int = 5, db: Session = Depends(get_db)):
    p = db.get(PickupModel, pickup_id)
    if not p: raise HTTPException(status_code=404, detail="Pickup not found")
    if p.lat is None or p.lon is None: return {"matches": [], "message": "Pickup coordinates are required for location matching"}
    matches=[]
    for c in db.scalars(select(UserModel).where(UserModel.role == Role.collector, UserModel.verified == True)).all():
        if c.lat is None or c.lon is None: continue
        d=distance_km(p.lat,p.lon,c.lat,c.lon)
        if d <= c.service_radius_km: matches.append({"collector":user_out(c),"distance_km":round(d,2)})
    matches.sort(key=lambda x:x["distance_km"])
    return {"matches":matches[:max(1,min(limit,20))]}

@app.patch("/api/pickups/{pickup_id}/assign/{collector_id}", response_model=PickupOut)
def assign_collector(pickup_id: int, collector_id: int, db: Session = Depends(get_db)):
    p=db.get(PickupModel,pickup_id); c=db.get(UserModel,collector_id)
    if not p: raise HTTPException(status_code=404,detail="Pickup not found")
    if not c or c.role != Role.collector: raise HTTPException(status_code=404,detail="Collector not found")
    if not c.verified: raise HTTPException(status_code=403,detail="Collector is not verified")
    p.collector_id=c.id; p.status=PickupStatus.assigned.value; db.commit(); db.refresh(p); return pickup_out(p)

@app.patch("/api/pickups/{pickup_id}/status", response_model=PickupOut)
def update_pickup_status(pickup_id: int, status: PickupStatus, db: Session = Depends(get_db)):
    p=db.get(PickupModel,pickup_id)
    if not p: raise HTTPException(status_code=404,detail="Pickup not found")
    p.status=status.value
    if status == PickupStatus.completed: p.completed_at=datetime.utcnow()
    db.commit(); db.refresh(p); return pickup_out(p)

@app.post("/api/pickups/{pickup_id}/weigh", response_model=PickupOut)
def record_weight(pickup_id: int, payload: WeightRecord, db: Session = Depends(get_db)):
    p=db.get(PickupModel,pickup_id)
    if not p: raise HTTPException(status_code=404,detail="Pickup not found")
    rate=price_for(p.material); amount=round(payload.actual_weight_kg*rate,2)
    p.actual_weight_kg=payload.actual_weight_kg; p.final_value=amount; p.status=PickupStatus.completed.value; p.completed_at=datetime.utcnow()
    db.add(Transaction(pickup_id=p.id,weight_kg=payload.actual_weight_kg,rate_per_kg=rate,amount_inr=amount,payment_method=payload.payment_method,status="recorded"))
    db.commit(); db.refresh(p); return pickup_out(p)

@app.get("/api/transactions")
def list_transactions(db:Session=Depends(get_db)):
    return [{"id":t.id,"pickup_id":t.pickup_id,"weight_kg":t.weight_kg,"rate_per_kg":t.rate_per_kg,"amount_inr":t.amount_inr,"payment_method":t.payment_method,"status":t.status,"recorded_at":t.recorded_at} for t in db.scalars(select(Transaction)).all()]

@app.post("/api/pickups/{pickup_id}/handoffs")
def create_handoff(pickup_id:int,payload:HandoffCreate,db:Session=Depends(get_db)):
    if not db.get(PickupModel,pickup_id): raise HTTPException(status_code=404,detail="Pickup not found")
    r=db.get(UserModel,payload.recycler_id)
    if not r or r.role != Role.recycler: raise HTTPException(status_code=404,detail="Recycler not found")
    h=RecyclerHandoff(pickup_id=pickup_id,**payload.model_dump()); db.add(h); db.commit(); db.refresh(h)
    return {"id":h.id,"pickup_id":h.pickup_id,"recycler_id":h.recycler_id,"quantity_kg":h.quantity_kg,"destination":h.destination,"notes":h.notes,"recorded_at":h.recorded_at}

@app.get("/api/handoffs")
def list_handoffs(db:Session=Depends(get_db)):
    return [{"id":h.id,"pickup_id":h.pickup_id,"recycler_id":h.recycler_id,"quantity_kg":h.quantity_kg,"destination":h.destination,"notes":h.notes,"recorded_at":h.recorded_at} for h in db.scalars(select(RecyclerHandoff)).all()]

@app.post("/api/quotes")
def quote(payload:PriceQuoteRequest):
    rate=price_for(payload.material); material=payload.material.lower().strip()
    return {"material":material,"rate_per_kg":rate,"weight_kg":payload.weight_kg,"estimated_value":round(rate*payload.weight_kg,2)}

@app.get("/api/impact")
def impact_metrics(db:Session=Depends(get_db)):
    pickups=db.scalars(select(PickupModel)).all(); users=db.scalars(select(UserModel)).all()
    completed=[p for p in pickups if p.status==PickupStatus.completed.value]
    by_material={}
    for p in completed: by_material[p.material]=round(by_material.get(p.material,0)+(p.actual_weight_kg or 0),2)
    return {"total_pickups":len(pickups),"completed_pickups":len(completed),"total_recycled_kg":round(sum(p.actual_weight_kg or 0 for p in completed),2),"total_value_inr":round(sum(p.final_value or 0 for p in completed),2),"material_breakdown_kg":by_material,"registered_collectors":sum(u.role==Role.collector for u in users),"registered_recyclers":sum(u.role==Role.recycler for u in users)}