CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20) NOT NULL UNIQUE,
  role VARCHAR(20) NOT NULL CHECK (role IN ('citizen','collector','recycler')),
  verified BOOLEAN NOT NULL DEFAULT FALSE,
  latitude DECIMAL(9,6),
  longitude DECIMAL(9,6),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pickups (
  id BIGSERIAL PRIMARY KEY,
  citizen_id BIGINT NOT NULL REFERENCES users(id),
  collector_id BIGINT REFERENCES users(id),
  material VARCHAR(50) NOT NULL,
  estimated_weight_kg DECIMAL(10,2) NOT NULL CHECK (estimated_weight_kg > 0),
  actual_weight_kg DECIMAL(10,2),
  address TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'requested',
  scheduled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE transactions (
  id BIGSERIAL PRIMARY KEY,
  pickup_id BIGINT NOT NULL REFERENCES pickups(id),
  weight_kg DECIMAL(10,2) NOT NULL CHECK (weight_kg > 0),
  rate_per_kg DECIMAL(10,2) NOT NULL,
  amount_inr DECIMAL(12,2) NOT NULL,
  recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE material_prices (
  material VARCHAR(50) PRIMARY KEY,
  rate_per_kg DECIMAL(10,2) NOT NULL CHECK (rate_per_kg >= 0),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);