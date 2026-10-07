from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.ticket import Ticket


class TicketDAO:

    def __init__(self, db: Session):
        self.db = db

    def save(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def find_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.db.get(Ticket, ticket_id)

    def find_all(self) -> list[Ticket]:
        return list(self.db.scalars(select(Ticket).order_by(Ticket.created_at)).all())