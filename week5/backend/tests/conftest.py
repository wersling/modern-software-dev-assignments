import os
import tempfile
from collections.abc import Generator

import pytest
from app.db import get_db
from app.main import app
from app.models import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    os.unlink(db_path)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """
    Fixture for direct database access in model tests.

    This provides a SQLAlchemy session for direct database operations
    without going through the FastAPI client. Useful for testing
    model constraints and database-level behavior.
    """
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    yield session

    session.close()
    os.unlink(db_path)
