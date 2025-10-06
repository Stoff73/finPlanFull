import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.database import get_db
from app.models.user import User
from passlib.context import CryptContext

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    # Create the database tables
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    # Drop the database tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def test_user():
    db = TestingSessionLocal()

    # Create a test user
    hashed_password = pwd_context.hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    db.delete(user)
    db.commit()
    db.close()


@pytest.fixture(scope="module")
def auth_headers(client, test_user):
    # Login to get access token
    response = client.post(
        "/api/auth/token",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}