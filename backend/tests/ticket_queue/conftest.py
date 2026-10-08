from datetime import date, datetime, timedelta

import pytest

from app.ticket_queue import (
    AllServicesPolicy,
    DailyServiceNumberGenerator,
    InMemoryEventBus,
    InMemoryTicketQueue,
    LongestQueueStrategy,
    QueueManager,
    ServiceType,
    Ticket,
)

BASE_TIME = datetime(2026, 10, 7, 9, 0, 0)


class FakeToday:
    """Controllable replacement for date.today."""

    def __init__(self, day: date = date(2026, 10, 7)) -> None:
        self.day = day

    def __call__(self) -> date:
        return self.day

    def advance(self, days: int = 1) -> None:
        self.day += timedelta(days=days)


@pytest.fixture
def make_ticket():
    def _make(code: int, service: ServiceType, seconds: int = 0) -> Ticket:
        return Ticket(code, service, BASE_TIME + timedelta(seconds=seconds))

    return _make


@pytest.fixture
def fake_today() -> FakeToday:
    return FakeToday()


@pytest.fixture
def bus() -> InMemoryEventBus:
    return InMemoryEventBus()


@pytest.fixture
def build_manager(bus, fake_today):
    """Build a QueueManager with in-memory parts; any part can be overridden."""

    def _build(**overrides) -> QueueManager:
        parts = {
            "queues": {service: InMemoryTicketQueue() for service in ServiceType},
            "bus": bus,
            "policy": AllServicesPolicy(),
            "strategy": LongestQueueStrategy(),
            "numbers": DailyServiceNumberGenerator(today=fake_today),
        }
        parts.update(overrides)
        return QueueManager(**parts)

    return _build


@pytest.fixture
def manager(build_manager) -> QueueManager:
    return build_manager()
