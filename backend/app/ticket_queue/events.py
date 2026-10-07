"""Events published on the EventBus. The event class is the topic."""
from dataclasses import dataclass

from .models import Ticket


@dataclass(frozen=True)
class TicketIssued:
    ticket: Ticket


@dataclass(frozen=True)
class TicketCalled:
    ticket: Ticket
    counter_id: str
