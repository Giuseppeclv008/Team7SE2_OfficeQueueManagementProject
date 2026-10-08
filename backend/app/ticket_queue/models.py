"""Domain types for the ticket queue.

Ticket mirrors the columns of the ticket table (app.models.Ticket), so a
queue ticket can be stored without translation. ServiceType and TicketStatus
are the shared enums from app.models.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.models.serviceType import ServiceType
from app.models.ticketStatus import TicketStatus

__all__ = ["ServiceType", "Ticket", "TicketStatus"]


@dataclass(frozen=True)
class Ticket:
    code: int  # per-service, restarts every day; see numbering.format_code for "X001"
    service_type: ServiceType
    created_at: datetime
    status: TicketStatus = TicketStatus.WAITING
    id: uuid.UUID = field(default_factory=uuid.uuid4)
