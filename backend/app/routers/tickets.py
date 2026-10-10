from datetime import date, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dao.ticket_dao import TicketDAO
from app.database import SessionLocal, get_db
from app.dto.ticket_dto import TicketCreateDTO, TicketResponseDTO
from app.models import ServiceType
from app.ticket_queue import (
    DailyServiceNumberGenerator,
    QueueManager,
    create_default_queue_manager,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _utc_today() -> date:
    # created_at is stored in UTC, so ticket days are UTC days too.
    return datetime.now(timezone.utc).date()


def _last_stored_code(service: ServiceType, day: date) -> int:
    with SessionLocal() as db:
        return TicketDAO(db).last_code(service, day)


# One manager for the whole app: queues and numbering are shared by all requests.
# Numbering resumes from the stored tickets, so a restart does not reuse codes.
_queue_manager = create_default_queue_manager(
    numbers=DailyServiceNumberGenerator(today=_utc_today, last_code=_last_stored_code)
)


def get_queue_manager() -> QueueManager:
    return _queue_manager


def get_ticket_dao(db: Annotated[Session, Depends(get_db)]) -> TicketDAO:
    return TicketDAO(db)


@router.post("", status_code=status.HTTP_201_CREATED, operation_id="NewTicket")
def new_ticket(
    body: TicketCreateDTO,
    manager: Annotated[QueueManager, Depends(get_queue_manager)],
    dao: Annotated[TicketDAO, Depends(get_ticket_dao)],
) -> TicketResponseDTO:
    """Issue a ticket for the requested service, queue it and store it."""
    ticket = manager.issue_ticket(body.service_type)
    return TicketResponseDTO.model_validate(dao.save(ticket))
