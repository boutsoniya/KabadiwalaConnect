from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20), index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    service_radius_km: Mapped[float] = mapped_column(Float, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Pickup(Base):
    __tablename__ = "pickups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    citizen_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    collector_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    material: Mapped[str] = mapped_column(String(40), index=True)
    estimated_weight_kg: Mapped[float] = mapped_column(Float)
    actual_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str] = mapped_column(String(500))
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="requested", index=True)
    estimated_value: Mapped[float] = mapped_column(Float, default=0)
    final_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class MaterialPrice(Base):
    __tablename__ = "material_prices"
    material: Mapped[str] = mapped_column(String(40), primary_key=True)
    rate_per_kg: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pickup_id: Mapped[int] = mapped_column(ForeignKey("pickups.id"), index=True)
    weight_kg: Mapped[float] = mapped_column(Float)
    rate_per_kg: Mapped[float] = mapped_column(Float)
    amount_inr: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    status: Mapped[str] = mapped_column(String(30), default="recorded")
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class RecyclerHandoff(Base):
    __tablename__ = "recycler_handoffs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pickup_id: Mapped[int] = mapped_column(ForeignKey("pickups.id"), index=True)
    recycler_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quantity_kg: Mapped[float] = mapped_column(Float)
    destination: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
