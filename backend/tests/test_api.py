import os

os.environ["DATABASE_URL"] = "sqlite:///./test_kabadiwala.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_user_and_pickup_flow():
    citizen = client.post('/api/users', json={'name': 'Demo Citizen', 'phone': '9999999999', 'role': 'citizen'}).json()
    collector = client.post('/api/users', json={'name': 'Demo Collector', 'phone': '8888888888', 'role': 'collector'}).json()
    assert collector['verified'] is False

    # Verify the collector through the database for the MVP assignment test.
    from app.database import SessionLocal
    from app.models import User
    with SessionLocal() as db:
        user = db.get(User, collector['id'])
        user.verified = True
        db.commit()

    pickup = client.post('/api/pickups', json={'citizen_id': citizen['id'], 'material': 'plastic', 'estimated_weight_kg': 5, 'address': 'Demo address'}).json()
    assert pickup['status'] == 'requested'
    assigned_response = client.patch(f"/api/pickups/{pickup['id']}/assign/{collector['id']}")
    assert assigned_response.status_code == 200
    assert assigned_response.json()['status'] == 'assigned'


def test_quote():
    response = client.post('/api/quotes', json={'material': 'plastic', 'weight_kg': 5})
    assert response.status_code == 200
    assert response.json()['estimated_value'] == 100.0