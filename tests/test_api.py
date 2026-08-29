import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_create_log():
    response = client.post(
        "/logs",
        json={
            "cigarettes": 1,
            "mood": "Stressed",
            "stress_level": 5,
            "location": "Home",
            "reason": "Work",
            "smoked_at": "2026-08-30T10:00:00"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Smoking log recieved successfully"
    assert "id" in data["data"]
    assert data["data"]["stress_level"] == 5

def test_create_log_invalid_stress_high():
    response = client.post(
        "/logs",
        json={
            "cigarettes": 1,
            "mood": "Stressed",
            "stress_level": 70,  # Invalid
            "location": "Home",
            "reason": "Work",
            "smoked_at": "2026-08-30T10:00:00"
        },
    )
    assert response.status_code == 422
    assert "Input should be less than or equal to 10" in response.text

def test_create_log_invalid_stress_low():
    response = client.post(
        "/logs",
        json={
            "cigarettes": 1,
            "mood": "Stressed",
            "stress_level": 0,  # Invalid
            "location": "Home",
            "reason": "Work",
            "smoked_at": "2026-08-30T10:00:00"
        },
    )
    assert response.status_code == 422
    assert "Input should be greater than or equal to 1" in response.text

def test_update_log():
    # Create
    create_response = client.post(
        "/logs",
        json={
            "cigarettes": 1,
            "mood": "Happy",
            "stress_level": 2,
            "location": "Bar",
            "reason": "Socializing",
            "smoked_at": "2026-08-30T10:00:00"
        },
    )
    log_id = create_response.json()["data"]["id"]

    # Update
    update_response = client.put(
        f"/logs/{log_id}",
        json={
            "cigarettes": 2,
            "mood": "Stressed",
            "stress_level": 8,
            "location": "Office",
            "reason": "Deadline",
            "smoked_at": "2026-08-30T12:00:00"
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["message"] == "Log updated sucessfully"
    assert data["data"]["cigarettes"] == 2
    assert data["data"]["stress_level"] == 8

def test_update_log_invalid_stress():
    # Create
    create_response = client.post(
        "/logs",
        json={
            "cigarettes": 1,
            "mood": "Happy",
            "stress_level": 2,
            "location": "Bar",
            "reason": "Socializing",
            "smoked_at": "2026-08-30T10:00:00"
        },
    )
    log_id = create_response.json()["data"]["id"]

    # Update with invalid stress
    update_response = client.put(
        f"/logs/{log_id}",
        json={
            "cigarettes": 2,
            "mood": "Stressed",
            "stress_level": 15, # Invalid
            "location": "Office",
            "reason": "Deadline",
            "smoked_at": "2026-08-30T12:00:00"
        },
    )
    assert update_response.status_code == 422

def test_delete_log():
    # Create
    create_response = client.post(
        "/logs",
        json={
            "cigarettes": 1,
            "mood": "Happy",
            "stress_level": 2,
            "location": "Bar",
            "reason": "Socializing",
            "smoked_at": "2026-08-30T10:00:00"
        },
    )
    log_id = create_response.json()["data"]["id"]

    # Delete
    delete_response = client.delete(f"/logs/{log_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Log Deleted sucessfully"

    # Verify deleted
    get_response = client.get("/logs")
    logs = get_response.json()
    assert len(logs) == 0