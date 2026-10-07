"""Abstractions the QueueManager depends on.

Each interface has a single responsibility. New behaviour is added by
writing a new implementation and injecting it, not by editing existing code.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from typing import Any

# change naming when integrating
from .models import ServiceType, Ticket

EventHandler = Callable[[Any], None]


class TicketQueue(ABC):
    """FIFO storage for the tickets of one service."""

    @abstractmethod
    def enqueue(self, ticket: Ticket) -> None: ...

    @abstractmethod
    def dequeue(self) -> Ticket | None:
        """Remove and return the oldest ticket, or None if empty."""

    @abstractmethod
    def peek(self) -> Ticket | None:
        """Return the oldest ticket without removing it, or None if empty."""

    @abstractmethod
    def __len__(self) -> int: ...


class EventBus(ABC):
    """Publish/subscribe delivery. Subscribers register per event class."""

    @abstractmethod
    def subscribe(self, event_type: type, handler: EventHandler) -> None: ...

    @abstractmethod
    def unsubscribe(self, event_type: type, handler: EventHandler) -> None: ...

    @abstractmethod
    def publish(self, event: object) -> None: ...


class CounterPolicy(ABC):
    """Business rule: which services a counter is allowed to serve."""

    @abstractmethod
    def eligible_services(self, counter_id: str) -> set[ServiceType]: ...


class SelectionStrategy(ABC):
    """Business rule: which queue a counter serves next."""

    @abstractmethod
    def select(self, queues: Mapping[ServiceType, TicketQueue]) -> ServiceType | None:
        """Return the service to serve next, or None if every queue is empty."""


class TicketNumberGenerator(ABC):
    @abstractmethod
    def next(self, service: ServiceType) -> int: ...
