CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('citizen','collector','recycler','admin')),
    password_hash VARCHAR(255),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    service_radius_km DOUBLE PRECISION NOT NULL DEFAULT 10,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pickups (
    id BIGSERIAL PRIMARY KEY,
    citizen_id BIGINT NOT NULL REFERENCES users(id),
    collector_id BIGINT REFERENCES users(id),
    material VARCHAR(50) NOT NULL,
    estimated_weight_kg DOUBLE PRECISION NOT NULL CHECK (estimated_weight_kg > 0),
    actual_weight_kg DOUBLE PRECISION,
    address TEXT NOT NULL,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    status VARCHAR(30) NOT NULL DEFAULT 'requested',
    estimated_value DOUBLE PRECISION NOT NULL DEFAULT 0,
    final_value DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    pickup_id BIGINT NOT NULL REFERENCES pickups(id),
    weight_kg DOUBLE PRECISION NOT NULL CHECK (weight_kg > 0),
    rate_per_kg DOUBLE PRECISION NOT NULL,
    amount_inr DOUBLE PRECISION NOT NULL,
    payment_method VARCHAR(30) DEFAULT 'cash',
    status VARCHAR(20) DEFAULT 'recorded',
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE material_prices (
    material VARCHAR(50) PRIMARY KEY,
    rate_per_kg DOUBLE PRECISION NOT NULL CHECK (rate_per_kg >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE recycler_handoffs (
    id BIGSERIAL PRIMARY KEY,
    pickup_id BIGINT NOT NULL REFERENCES pickups(id),
    recycler_id BIGINT NOT NULL REFERENCES users(id),
    quantity_kg DOUBLE PRECISION NOT NULL CHECK (quantity_kg > 0),
    destination VARCHAR(200) NOT NULL,
    notes TEXT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pickups_status ON pickups(status);
CREATE INDEX idx_pickups_collector ON pickups(collector_id);
CREATE INDEX idx_pickups_citizen ON pickups(citizen_id);
CREATE INDEX idx_handoffs_pickup ON recycler_handoffs(pickup_id);