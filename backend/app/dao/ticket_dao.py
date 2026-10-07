from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.dto.ticket_dto import TicketCreateDTO
from app.models.ticket import Ticket
from app.models.ticketStatus import TicketStatus


class TicketDAO:

    def __init__(self, db: Session):
        self.db = db

    def create(self, ticket_in: TicketCreateDTO) -> Ticket:
        # Calcola il prossimo numero (ripartendo da 1 ogni giorno)
        max_code = self.db.scalar(
            select(func.max(Ticket.code)).where(
                func.date(Ticket.created_at) == func.current_date()
            )
        )
        next_code = (max_code or 0) + 1

        new_ticket = Ticket(
            code=next_code,
            service_type=ticket_in.service_type,
            status=TicketStatus.WAITING,
        )
        self.db.add(new_ticket)
        self.db.commit()
        self.db.refresh(new_ticket)
        return new_ticket

    def find_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.db.get(Ticket, ticket_id)

    def find_all(self) -> list[Ticket]:
        return list(self.db.scalars(select(Ticket).order_by(Ticket.created_at)).all())