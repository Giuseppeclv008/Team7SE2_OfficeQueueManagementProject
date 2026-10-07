"""Ticket queue for the Office Queue Management system.

Usage from the API layer:

    from app.ticket_queue import create_default_queue_manager, format_code, TicketCalled

    manager = create_default_queue_manager()
    manager.events.subscribe(TicketCalled, on_called)
    ticket = manager.issue_ticket("boxes")      # "get ticket" button
    called = manager.call_next(counter_id="1")  # "call next" button
    format_code(called.service_type, called.code)  # "X001" for the display
"""
from .events import TicketCalled, TicketIssued
from .exceptions import QueueError, UnknownCounterError
from .in_memory import InMemoryEventBus, InMemoryTicketQueue
from .interfaces import (
    CounterPolicy,
    EventBus,
    EventHandler,
    SelectionStrategy,
    TicketNumberGenerator,
    TicketQueue,
)
from .models import ServiceType, Ticket, TicketStatus
from .numbering import DEFAULT_PREFIXES, DailyServiceNumberGenerator, format_code
from .policies import AllServicesPolicy
from .queue_manager import QueueManager
from .strategies import LongestQueueStrategy

__all__ = [
    "AllServicesPolicy",
    "DEFAULT_PREFIXES",
    "DailyServiceNumberGenerator",
    "CounterPolicy",
    "EventBus",
    "EventHandler",
    "InMemoryEventBus",
    "InMemoryTicketQueue",
    "LongestQueueStrategy",
    "QueueError",
    "QueueManager",
    "SelectionStrategy",
    "ServiceType",
    "Ticket",
    "TicketCalled",
    "TicketIssued",
    "TicketNumberGenerator",
    "TicketQueue",
    "TicketStatus",
    "UnknownCounterError",
    "create_default_queue_manager",
    "format_code",
]


def create_default_queue_manager() -> QueueManager:
    """In-memory manager: one queue per ServiceType, every counter serves every service."""
    return QueueManager(
        queues={service: InMemoryTicketQueue() for service in ServiceType},
        bus=InMemoryEventBus(),
        policy=AllServicesPolicy(),
        strategy=LongestQueueStrategy(),
        numbers=DailyServiceNumberGenerator(),
    )
