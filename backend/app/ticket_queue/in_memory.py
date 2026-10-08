"""In-memory implementations. State lives in the process and is lost on restart."""
import logging
from collections import defaultdict, deque

from .interfaces import EventBus, EventHandler, TicketQueue
from .models import Ticket

logger = logging.getLogger(__name__)


class InMemoryTicketQueue(TicketQueue):
    def __init__(self) -> None:
        self._tickets: deque[Ticket] = deque()

    def enqueue(self, ticket: Ticket) -> None:
        self._tickets.append(ticket)

    def dequeue(self) -> Ticket | None:
        return self._tickets.popleft() if self._tickets else None

    def peek(self) -> Ticket | None:
        return self._tickets[0] if self._tickets else None

    def __len__(self) -> int:
        return len(self._tickets)


class InMemoryEventBus(EventBus):
    """Synchronous bus: publish() calls every handler of the event's class in order."""

    def __init__(self) -> None:
        self._handlers: defaultdict[type, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: object) -> None:
        # Copy so a handler that (un)subscribes during delivery is safe.
        for handler in list(self._handlers.get(type(event), [])):
            try:
                handler(event)
            except Exception:
                logger.exception("Event handler %r failed for %r", handler, event)
