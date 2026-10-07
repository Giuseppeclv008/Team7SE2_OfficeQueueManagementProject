# Importa qui tutti i modelli, così Alembic li trova per l'autogenerate.
from app.models.ticket import Ticket
from app.models.serviceType import ServiceType
from app.models.ticketStatus import TicketStatus

__all__ = ["Ticket", "ServiceType", "TicketStatus"]
