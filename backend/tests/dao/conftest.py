import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  registers every table on Base.metadata
from app.dao.customer_dao import CustomerDAO
from app.dao.officer_dao import OfficerDAO
from app.database import Base


@pytest.fixture(autouse=True)
def reset_mock_daos():
    """Mock DAO storage is shared by all instances: start every test from the seed data."""
    CustomerDAO.reset()
    OfficerDAO.reset()
    yield
    CustomerDAO.reset()
    OfficerDAO.reset()


@pytest.fixture
def db() -> Session:
    """Fresh in-memory SQLite database per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session
    engine.dispose()
