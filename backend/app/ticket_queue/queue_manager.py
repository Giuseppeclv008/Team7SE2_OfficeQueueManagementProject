"""Facade used by the API layer.

Issued tickets are WAITING; call_next returns the ticket as IN_PROGRESS.

issue_ticket() runs when a customer clicks "get ticket" (enqueue).
call_next() runs when an officer clicks "call next" (dequeue).
"""
import threading
from collections.abc import Mapping
from dataclasses import replace
from datetime import datetime, timezone

from .events import TicketCalled, TicketIssued
from .interfaces import (
    CounterPolicy,
    EventBus,
    SelectionStrategy,
    TicketNumberGenerator,
    TicketQueue,
)
from .models import ServiceType, Ticket, TicketStatus


class QueueManager:
    def __init__(
        self,
        queues: Mapping[ServiceType, TicketQueue],
        bus: EventBus,
        policy: CounterPolicy,
        strategy: SelectionStrategy,
        numbers: TicketNumberGenerator,
    ) -> None:
        self._queues = dict(queues)
        self._bus = bus
        self._policy = policy
        self._strategy = strategy
        self._numbers = numbers
        self._lock = threading.Lock()

    @property
    def events(self) -> EventBus:
        """Bus to subscribe to TicketIssued / TicketCalled (e.g. UI display)."""
        return self._bus

    def issue_ticket(self, service: ServiceType | str) -> Ticket:
        service = ServiceType(service)  # ValueError for unknown values
        if service not in self._queues:
            raise ValueError(f"No queue configured for service {service.value!r}")

        with self._lock:
            ticket = Ticket(
                code=self._numbers.next(service),
                service_type=service,
                created_at=datetime.now(timezone.utc),
            )
            self._queues[service].enqueue(ticket)

        self._bus.publish(TicketIssued(ticket))
        return ticket

    def call_next(self, counter_id: str) -> Ticket | None:
        with self._lock:
            eligible = self._policy.eligible_services(counter_id)
            candidates = {s: q for s, q in self._queues.items() if s in eligible}
            service = self._strategy.select(candidates)
            if service is None:
                return None
            ticket = replace(self._queues[service].dequeue(), status=TicketStatus.IN_PROGRESS)

        self._bus.publish(TicketCalled(ticket, counter_id))
        return ticket

    def queue_lengths(self) -> dict[ServiceType, int]:
        with self._lock:
            return {service: len(queue) for service, queue in self._queues.items()}
