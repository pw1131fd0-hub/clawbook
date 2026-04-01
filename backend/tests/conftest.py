"""Pytest configuration and shared fixtures for ClawBook backend tests."""
import os
import tempfile
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import Base, get_db


# Create a temporary SQLite database for testing
@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine with a temporary file."""
    import tempfile

    # Create a temporary file
    fd, temp_db = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Create engine with the temporary file
    database_url = f"sqlite:///{temp_db}"
    engine = create_engine(database_url, echo=False)

    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables
    Base.metadata.create_all(engine)

    yield engine

    # Clean up - close engine and delete temp file
    engine.dispose()
    try:
        os.unlink(temp_db)
    except Exception:
        pass


@pytest.fixture(scope="function")
def db(db_engine) -> Session:
    """Create a test database session."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """Create a test client with overridden database dependency."""
    def override_get_db():
        yield db

    # Store any existing overrides to restore them later
    existing_overrides = app.dependency_overrides.copy()

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    yield test_client

    # Restore previous overrides or clear if there were none
    app.dependency_overrides.clear()
    app.dependency_overrides.update(existing_overrides)
