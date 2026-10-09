from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.serviceType import ServiceType
from app.models.ticket import Ticket
from app.ticket_queue.models import Ticket as QueueTicket


class TicketDAO:

    def __init__(self, db: Session):
        self.db = db

    def save(self, ticket: Ticket | QueueTicket) -> Ticket:
        if not isinstance(ticket, Ticket):
            ticket = Ticket(
                id=ticket.id,
                code=ticket.code,
                service_type=ticket.service_type,
                status=ticket.status,
                created_at=ticket.created_at,
            )
        self.db.add(ticket)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(ticket)
        return ticket

    def find_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.db.get(Ticket, ticket_id)

    def find_all(self) -> list[Ticket]:
        return list(
            self.db.scalars(
                select(Ticket).order_by(Ticket.created_at, Ticket.code)
            ).all()
        )

    def last_code(self, service: ServiceType, day: date) -> int:
        """Highest code issued for a service on a UTC day, or 0 if none."""
        start = datetime.combine(day, time.min, tzinfo=timezone.utc)
        last = self.db.scalar(
            select(func.max(Ticket.code)).where(
                Ticket.service_type == service,
                Ticket.created_at >= start,
                Ticket.created_at < start + timedelta(days=1),
            )
        )
        return last or 0
