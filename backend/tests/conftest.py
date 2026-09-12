import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
import app.db.session as db_session
from app.db.session import get_db

from fastapi.testclient import TestClient

# Use a single in-memory SQLite DB shared across threads for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Replace the app's DB engine and SessionLocal so the running app uses the test DB
db_session.engine = engine
db_session.SessionLocal = TestingSessionLocal

# Import models so they register with Base.metadata before creating tables
import app.models.user  # noqa: F401
import app.models.profile  # noqa: F401
import app.models.service  # noqa: F401
import app.models.project  # noqa: F401
import app.models.portfolio  # noqa: F401
import app.models.invitation  # noqa: F401
import app.models.milestone  # noqa: F401
import app.models.task  # noqa: F401
import app.models.file  # noqa: F401
import app.models.workspace  # noqa: F401
import app.models.delivery  # noqa: F401
import app.models.payment  # noqa: F401
import app.models.notification  # noqa: F401
import app.models.notification_preference  # noqa: F401
import app.models.chat  # noqa: F401
import app.models.dispute  # noqa: F401
import app.models.withdrawal  # noqa: F401

# Create all tables
Base.metadata.create_all(bind=engine)

# Import app after wiring DB
from app.main import create_app
app = create_app()


@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    Base.metadata.create_all(bind=db.bind)

    yield db

    # Clean up: rollback and clear all tables for next test
    db.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(text(f"DELETE FROM {table.name}"))
    db.commit()
    db.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Clean up overrides after test
    app.dependency_overrides.pop(get_db, None)
