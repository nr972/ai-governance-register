import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.database import Base, get_db
from api.main import app

TEST_DATABASE_URL = "sqlite://"


@pytest.fixture()
def db_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    yield session
    session.close()


@pytest.fixture()
def client(db_engine):
    session_factory = sessionmaker(bind=db_engine)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_system_data():
    return {
        "name": "Test AI System",
        "description": "A test AI system for unit testing purposes.",
        "purpose": "Automated testing of the governance register.",
        "use_case_category": "general_purpose",
        "risk_tier": "minimal",
        "responsible_team": "Test Team",
        "contact_email": "test@example.com",
    }


@pytest.fixture()
def created_system(client, sample_system_data):
    resp = client.post("/api/systems", json=sample_system_data)
    assert resp.status_code == 201
    return resp.json()
