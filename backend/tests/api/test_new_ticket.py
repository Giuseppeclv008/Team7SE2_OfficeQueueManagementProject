from datetime import datetime, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dao.ticket_dao import TicketDAO
from app.main import app
from app.models import Ticket
from app.routers.tickets import get_queue_manager, get_ticket_dao
from app.ticket_queue import (
    DailyServiceNumberGenerator,
    ServiceType,
    TicketStatus,
    create_default_queue_manager,
)


def make_manager(db: Session):
    """What the app builds at startup, reading previous codes from the test database."""
    return create_default_queue_manager(
        numbers=DailyServiceNumberGenerator(
            today=lambda: datetime.now(timezone.utc).date(),
            last_code=TicketDAO(db).last_code,
        )
    )


@pytest.fixture
def manager(db):
    return make_manager(db)


@pytest.fixture
def client(db: Session, manager):
    app.dependency_overrides[get_ticket_dao] = lambda: TicketDAO(db)
    app.dependency_overrides[get_queue_manager] = lambda: manager
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_new_ticket_returns_a_waiting_ticket(client):
    response = client.post("/tickets", json={"service_type": "boxes"})

    assert response.status_code == 201
    body = response.json()
    assert (body["code"], body["service_type"], body["status"]) == (1, "boxes", "waiting")


def test_new_ticket_is_stored(client, db):
    body = client.post("/tickets", json={"service_type": "bills_payment"}).json()

    row = db.scalars(select(Ticket)).one()
    assert str(row.id) == body["id"]
    assert row.service_type == ServiceType.BILLS_PAYMENT


def test_new_ticket_is_queued(client, manager):
    client.post("/tickets", json={"service_type": "boxes"})
    client.post("/tickets", json={"service_type": "boxes"})

    assert manager.queue_lengths()[ServiceType.BOXES] == 2


def test_codes_are_numbered_per_service(client):
    codes = [
        (t["service_type"], t["code"])
        for t in (client.post("/tickets", json={"service_type": s}).json()
                  for s in ("boxes", "boxes", "account_management"))
    ]

    assert codes == [("boxes", 1), ("boxes", 2), ("account_management", 1)]


@pytest.mark.parametrize("body", [{"service_type": "unknown"}, {"service_type": "BOXES"}, {}])
def test_invalid_service_type_is_rejected(client, db, manager, body):
    response = client.post("/tickets", json=body)

    assert response.status_code == 422
    assert db.scalar(select(func.count()).select_from(Ticket)) == 0
    assert sum(manager.queue_lengths().values()) == 0


def test_numbering_continues_after_a_restart(client, db):
    client.post("/tickets", json={"service_type": "boxes"})
    client.post("/tickets", json={"service_type": "boxes"})

    restarted = make_manager(db)
    app.dependency_overrides[get_queue_manager] = lambda: restarted
    response = client.post("/tickets", json={"service_type": "boxes"})

    assert response.json()["code"] == 3


# Checks the customer-visible HTTP response without inspecting internal app state.
def test_get_ticket_black_box_http_contract(client):
    """Check the customer-visible behavior without inspecting app internals."""
    response = client.post("/tickets", json={"service_type": "boxes"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["code"] == 1
    assert body["service_type"] == "boxes"
    assert body["status"] == "waiting"
    assert body["created_at"]


# Checks the route, queue manager, and database together, then calls manager.call_next() and verifies the ticket leaves the in-memory queue.
def test_get_ticket_white_box_connects_route_queue_and_database(client, manager, db):
    """Trace one issued ticket through the endpoint, queue manager, and DAO."""
    response = client.post("/tickets", json={"service_type": "bills_payment"})
    assert response.status_code == 201
    body = response.json()

    service = ServiceType.BILLS_PAYMENT
    assert manager.queue_lengths()[service] == 1

    stored = db.scalars(select(Ticket).where(Ticket.id == UUID(body["id"]))).one()
    assert stored.code == body["code"]
    assert stored.service_type is service
    assert stored.status is TicketStatus.WAITING

    called = manager.call_next("counter-1")
    assert called is not None
    assert str(called.id) == body["id"]
    assert called.code == stored.code
    assert called.service_type is stored.service_type
    assert called.status is TicketStatus.IN_PROGRESS
    assert manager.queue_lengths()[service] == 0
