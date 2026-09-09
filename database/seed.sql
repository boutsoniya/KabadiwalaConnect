INSERT INTO material_prices(material, rate_per_kg) VALUES
('paper', 12.00),
('plastic', 20.00),
('cardboard', 10.00),
('metal', 35.00),
('glass', 8.00),
('ewaste', 70.00)
ON CONFLICT (material) DO UPDATE SET rate_per_kg = EXCLUDED.rate_per_kg, updated_at = NOW();