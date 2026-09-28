"""Pytest fixtures for unit, integration, and API testing."""

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.database import Base
from app.main import app
from app.models.user import User
from app.utils.security import create_access_token, get_password_hash

# In-memory SQLite for isolated test execution
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test tables once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a transactional database session for tests, rolled back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a TestClient with database session overridden."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Fixture providing an admin user in the test database."""
    user = User(
        email="test_admin@example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Test Admin",
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_user(db_session: Session) -> User:
    """Fixture providing a standard user in the test database."""
    user = User(
        email="test_user@example.com",
        hashed_password=get_password_hash("UserPass123!"),
        full_name="Standard User",
        role="user",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token_headers(admin_user: User) -> dict:
    """Authorization headers for admin user."""
    token = create_access_token({"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_token_headers(normal_user: User) -> dict:
    """Authorization headers for normal user."""
    token = create_access_token({"sub": str(normal_user.id), "email": normal_user.email, "role": "user"})
    return {"Authorization": f"Bearer {token}"}
