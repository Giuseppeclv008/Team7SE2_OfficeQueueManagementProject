from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.ticket import Ticket


class TicketDAO:

    def __init__(self, db: Session):
        self.db = db

    def save(self, ticket: Ticket) -> Ticket:
        try:
            self.db.add(ticket)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(ticket)
        return ticket

    def find_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.db.get(Ticket, ticket_id)

    def find_all(self) -> list[Ticket]:
        stmt = select(Ticket).order_by(Ticket.created_at, Ticket.code)
        return list(self.db.scalars(stmt).all())