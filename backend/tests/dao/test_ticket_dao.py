import uuid
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.dao.ticket_dao import TicketDAO
from app.models import ServiceType, Ticket, TicketStatus
from app.ticket_queue import create_default_queue_manager

S = ServiceType


def make_ticket(code: int = 1, service: ServiceType = S.BOXES, **fields) -> Ticket:
    return Ticket(code=code, service_type=service, status=TicketStatus.WAITING, **fields)


# --- save -------------------------------------------------------------------


def test_save_persists_ticket_and_returns_it(db):
    dao = TicketDAO(db)
    ticket = make_ticket(code=7, service=S.BILLS_PAYMENT)

    saved = dao.save(ticket)

    assert saved is ticket
    assert isinstance(saved.id, uuid.UUID)
    assert saved.code == 7
    assert saved.service_type is S.BILLS_PAYMENT
    assert saved.status is TicketStatus.WAITING


def test_save_fills_created_at_from_database_default(db):
    saved = TicketDAO(db).save(make_ticket())

    assert isinstance(saved.created_at, datetime)


def test_save_keeps_explicit_id_and_created_at(db):
    ticket_id = uuid.uuid4()
    created_at = datetime(2026, 10, 7, 9, 30)

    saved = TicketDAO(db).save(make_ticket(id=ticket_id, created_at=created_at))

    assert saved.id == ticket_id
    assert saved.created_at == created_at


def test_save_commits_so_ticket_is_visible_after_rollback(db):
    ticket_id = TicketDAO(db).save(make_ticket()).id
    db.rollback()
    db.expunge_all()

    assert db.get(Ticket, ticket_id) is not None


def test_save_gives_distinct_ids(db):
    dao = TicketDAO(db)

    first = dao.save(make_ticket(code=1))
    second = dao.save(make_ticket(code=2))

    assert first.id != second.id


def test_save_queue_ticket_round_trip(db):
    """A ticket from QueueManager.issue_ticket maps 1:1 onto the DB model."""
    issued = create_default_queue_manager().issue_ticket(S.ACCOUNT_MANAGEMENT)

    TicketDAO(db).save(
        Ticket(
            id=issued.id,
            code=issued.code,
            service_type=issued.service_type,
            status=issued.status,
            created_at=issued.created_at.replace(tzinfo=None),
        )
    )
    db.expunge_all()
    stored = TicketDAO(db).find_by_id(issued.id)

    assert stored.code == issued.code == 1
    assert stored.service_type is S.ACCOUNT_MANAGEMENT
    assert stored.status is TicketStatus.WAITING


# --- find_by_id -------------------------------------------------------------


def test_find_by_id_returns_saved_ticket(db):
    dao = TicketDAO(db)
    saved = dao.save(make_ticket(code=3, service=S.BOXES))
    db.expunge_all()

    found = dao.find_by_id(saved.id)

    assert found is not None
    assert found.id == saved.id
    assert found.code == 3
    assert found.service_type is S.BOXES


def test_find_by_id_returns_none_for_unknown_id(db):
    dao = TicketDAO(db)
    dao.save(make_ticket())

    assert dao.find_by_id(uuid.uuid4()) is None


# --- find_all ---------------------------------------------------------------


def test_find_all_returns_empty_list_when_no_tickets(db):
    assert TicketDAO(db).find_all() == []


def test_find_all_returns_tickets_ordered_by_created_at(db):
    dao = TicketDAO(db)
    late = dao.save(make_ticket(code=1, created_at=datetime(2026, 10, 7, 11, 0)))
    early = dao.save(make_ticket(code=2, created_at=datetime(2026, 10, 7, 9, 0)))
    middle = dao.save(make_ticket(code=3, created_at=datetime(2026, 10, 7, 10, 0)))

    assert [t.id for t in dao.find_all()] == [early.id, middle.id, late.id]


def test_find_all_returns_tickets_of_every_service(db):
    dao = TicketDAO(db)
    for service in ServiceType:
        dao.save(make_ticket(service=service))

    assert {t.service_type for t in dao.find_all()} == set(ServiceType)


# --- known bugs (code review) -----------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="SQLite strips tzinfo even with DateTime(timezone=True).",
)
def test_bug_created_at_loses_utc_timezone(db):
    issued = create_default_queue_manager().issue_ticket(S.BOXES)
    dao = TicketDAO(db)
    dao.save(
        Ticket(
            id=issued.id,
            code=issued.code,
            service_type=issued.service_type,
            status=issued.status,
            created_at=issued.created_at,
        )
    )
    db.expunge_all()

    stored = dao.find_by_id(issued.id)

    assert stored.created_at.tzinfo is not None
    assert stored.created_at == issued.created_at


def test_bug_save_rejects_queue_ticket(db):
    issued = create_default_queue_manager().issue_ticket(S.BOXES)
    dao = TicketDAO(db)

    dao.save(issued)

    assert dao.find_by_id(issued.id).code == issued.code


def test_bug_failed_save_leaves_session_unusable(db):
    dao = TicketDAO(db)
    first = dao.save(make_ticket(code=1))
    db.expunge_all()

    with pytest.raises(IntegrityError):
        dao.save(make_ticket(code=2, id=first.id))  # duplicate primary key

    assert [t.code for t in dao.find_all()] == [1]


def test_bug_find_all_order_undefined_for_equal_created_at(db):
    same_time = datetime(2026, 10, 8, 9, 0)
    dao = TicketDAO(db)
    for code in (3, 1, 2):
        dao.save(make_ticket(code=code, created_at=same_time))

    assert [t.code for t in dao.find_all()] == [1, 2, 3]