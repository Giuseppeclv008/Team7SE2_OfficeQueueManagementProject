import threading

import pytest

from app.ticket_queue import (
    CounterPolicy,
    QueueManager,
    ServiceType,
    TicketCalled,
    TicketIssued,
    TicketStatus,
    UnknownCounterError,
    create_default_queue_manager,
    format_code,
)

S = ServiceType


class OnlyServicesPolicy(CounterPolicy):
    """Test policy: counters may serve only the services in the mapping."""

    def __init__(self, mapping):
        self.mapping = mapping

    def eligible_services(self, counter_id):
        if counter_id not in self.mapping:
            raise UnknownCounterError(counter_id)
        return self.mapping[counter_id]


# --- issue_ticket ---------------------------------------------------------


def test_issue_ticket_returns_waiting_ticket_for_service(manager):
    ticket = manager.issue_ticket(S.BOXES)

    assert ticket.code == 1
    assert ticket.service_type is S.BOXES
    assert ticket.status is TicketStatus.WAITING
    assert ticket.created_at.tzinfo is not None


def test_issued_tickets_get_distinct_ids(manager):
    first = manager.issue_ticket(S.BOXES)
    second = manager.issue_ticket(S.BILLS_PAYMENT)

    assert first.id != second.id


def test_issue_ticket_accepts_service_value_string(manager):
    ticket = manager.issue_ticket("bills_payment")

    assert ticket.service_type is S.BILLS_PAYMENT
    assert ticket.code == 1


def test_issue_ticket_enqueues_on_the_service_queue(manager):
    manager.issue_ticket(S.BOXES)
    manager.issue_ticket(S.BOXES)
    manager.issue_ticket(S.ACCOUNT_MANAGEMENT)

    assert manager.queue_lengths() == {
        S.BOXES: 2,
        S.BILLS_PAYMENT: 0,
        S.ACCOUNT_MANAGEMENT: 1,
    }


def test_issue_ticket_publishes_ticket_issued(manager):
    events = []
    manager.events.subscribe(TicketIssued, events.append)

    ticket = manager.issue_ticket(S.BOXES)

    assert events == [TicketIssued(ticket)]


def test_issue_ticket_rejects_unknown_service_without_side_effects(manager):
    events = []
    manager.events.subscribe(TicketIssued, events.append)

    with pytest.raises(ValueError):
        manager.issue_ticket("coffee")

    assert events == []
    assert sum(manager.queue_lengths().values()) == 0
    assert manager.issue_ticket(S.BOXES).code == 1


def test_issue_ticket_rejects_service_without_configured_queue(build_manager):
    manager = build_manager(queues={})

    with pytest.raises(ValueError):
        manager.issue_ticket(S.BOXES)


def test_failing_subscriber_does_not_break_issue_ticket(manager):
    def failing(event):
        raise RuntimeError("boom")

    manager.events.subscribe(TicketIssued, failing)

    ticket = manager.issue_ticket(S.BOXES)

    assert ticket.code == 1
    assert manager.queue_lengths()[S.BOXES] == 1


# --- call_next ------------------------------------------------------------


def test_call_next_returns_none_when_nobody_is_waiting(manager):
    events = []
    manager.events.subscribe(TicketCalled, events.append)

    assert manager.call_next("1") is None
    assert events == []


def test_call_next_dequeues_and_publishes_ticket_called(manager):
    events = []
    manager.events.subscribe(TicketCalled, events.append)
    ticket = manager.issue_ticket(S.BOXES)

    called = manager.call_next("3")

    assert called.id == ticket.id
    assert events == [TicketCalled(called, "3")]
    assert manager.queue_lengths()[S.BOXES] == 0


def test_call_next_returns_ticket_in_progress_with_same_data(manager):
    ticket = manager.issue_ticket(S.BOXES)

    called = manager.call_next("1")

    assert called.status is TicketStatus.IN_PROGRESS
    assert (called.id, called.code, called.service_type, called.created_at) == (
        ticket.id,
        ticket.code,
        ticket.service_type,
        ticket.created_at,
    )
    assert ticket.status is TicketStatus.WAITING


def test_call_next_serves_longest_queue_first(manager):
    manager.issue_ticket(S.BOXES)
    manager.issue_ticket(S.BILLS_PAYMENT)
    manager.issue_ticket(S.BILLS_PAYMENT)

    called = manager.call_next("1")
    assert (called.service_type, called.code) == (S.BILLS_PAYMENT, 1)


def test_call_next_tie_serves_oldest_waiting_ticket(manager):
    manager.issue_ticket(S.BOXES)
    manager.issue_ticket(S.BILLS_PAYMENT)

    assert manager.call_next("1").service_type is S.BOXES
    assert manager.call_next("1").service_type is S.BILLS_PAYMENT


def test_call_next_drains_every_queue_then_returns_none(manager):
    issued = {manager.issue_ticket(service).id for service in ServiceType for _ in range(2)}

    called = set()
    while (ticket := manager.call_next("1")) is not None:
        called.add(ticket.id)

    assert called == issued
    assert manager.call_next("1") is None


def test_call_next_only_serves_services_allowed_by_policy(build_manager):
    manager = build_manager(policy=OnlyServicesPolicy({"1": {S.ACCOUNT_MANAGEMENT}}))
    manager.issue_ticket(S.BOXES)
    manager.issue_ticket(S.BOXES)
    manager.issue_ticket(S.ACCOUNT_MANAGEMENT)

    assert manager.call_next("1").service_type is S.ACCOUNT_MANAGEMENT
    assert manager.call_next("1") is None
    assert manager.queue_lengths()[S.BOXES] == 2


def test_call_next_propagates_policy_error_and_keeps_working(build_manager):
    manager = build_manager(policy=OnlyServicesPolicy({"1": set(ServiceType)}))
    manager.issue_ticket(S.BOXES)

    with pytest.raises(UnknownCounterError):
        manager.call_next("99")

    assert manager.call_next("1").code == 1


# --- events are published outside the lock --------------------------------


def run_with_timeout(fn, timeout=2.0):
    """Run fn in a daemon thread; return True if it finished in time."""
    thread = threading.Thread(target=fn, daemon=True)
    thread.start()
    thread.join(timeout)
    return not thread.is_alive()


@pytest.mark.parametrize("event_type", [TicketIssued, TicketCalled])
def test_subscribers_can_use_the_manager_while_handling_events(manager, event_type):
    finished = []

    def handler(event):
        # Would deadlock if the manager published while holding its lock.
        finished.append(run_with_timeout(manager.queue_lengths))

    manager.events.subscribe(event_type, handler)
    manager.issue_ticket(S.BOXES)
    manager.call_next("1")

    assert finished == [True]


# --- day rollover ---------------------------------------------------------


def test_numbers_restart_next_day_while_queues_keep_waiting_tickets(manager, fake_today):
    manager.issue_ticket(S.BOXES)
    fake_today.advance()

    new_ticket = manager.issue_ticket(S.BOXES)

    assert new_ticket.code == 1
    assert manager.queue_lengths()[S.BOXES] == 2


# --- concurrency ----------------------------------------------------------


def test_concurrent_issue_ticket_gives_unique_codes_per_service(manager):
    per_thread = 100
    services = list(ServiceType) * 4
    numbers = []
    lock = threading.Lock()

    def worker(service):
        for _ in range(per_thread):
            ticket = manager.issue_ticket(service)
            with lock:
                numbers.append((ticket.service_type, ticket.code))

    threads = [threading.Thread(target=worker, args=(s,)) for s in services]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(numbers) == len(services) * per_thread
    assert len(set(numbers)) == len(numbers)
    for service in ServiceType:
        codes = sorted(code for s, code in numbers if s is service)
        assert codes == list(range(1, 4 * per_thread + 1))
    assert sum(manager.queue_lengths().values()) == len(numbers)


def test_concurrent_call_next_serves_each_ticket_once(manager):
    issued = [manager.issue_ticket(s).id for s in ServiceType for _ in range(200)]
    called = []
    lock = threading.Lock()

    def officer(counter_id):
        while (ticket := manager.call_next(counter_id)) is not None:
            with lock:
                called.append(ticket.id)

    threads = [threading.Thread(target=officer, args=(str(i),)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(called) == sorted(issued)


# --- factory --------------------------------------------------------------


def test_default_factory_builds_working_manager():
    manager = create_default_queue_manager()

    assert isinstance(manager, QueueManager)
    assert manager.queue_lengths() == {service: 0 for service in ServiceType}
    ticket = manager.issue_ticket(S.ACCOUNT_MANAGEMENT)
    assert format_code(ticket.service_type, ticket.code) == "A001"
    assert manager.call_next("1").id == ticket.id
