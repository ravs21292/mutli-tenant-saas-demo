"""
Authentication tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_tenant(setup_database):
    db = TestingSessionLocal()
    tenant = Tenant(
        name="Test Tenant",
        subdomain="test",
        subscription_plan="basic",
        subscription_status="active"
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    yield tenant
    db.close()

@pytest.fixture
def test_user(setup_database, test_tenant):
    db = TestingSessionLocal()
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        first_name="Test",
        last_name="User",
        tenant_id=test_tenant.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()

def test_login_success(test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_register_success(test_tenant):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User",
            "tenant_id": str(test_tenant.id)
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"

def test_register_duplicate_email(test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "anotheruser",
            "password": "password",
            "first_name": "Another",
            "last_name": "User",
            "tenant_id": str(test_user.tenant_id)
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
