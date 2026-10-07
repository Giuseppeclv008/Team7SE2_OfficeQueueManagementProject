from app.ticket_queue import InMemoryTicketQueue, LongestQueueStrategy, ServiceType

S = ServiceType


def empty_queues():
    return {service: InMemoryTicketQueue() for service in ServiceType}


def test_returns_none_when_all_queues_are_empty():
    assert LongestQueueStrategy().select(empty_queues()) is None


def test_returns_none_when_no_queues_are_given():
    assert LongestQueueStrategy().select({}) is None


def test_selects_the_longest_queue(make_ticket):
    queues = empty_queues()
    queues[S.BOXES].enqueue(make_ticket("X001", S.BOXES, seconds=0))
    queues[S.BILLS_PAYMENT].enqueue(make_ticket("B001", S.BILLS_PAYMENT, seconds=1))
    queues[S.BILLS_PAYMENT].enqueue(make_ticket("B002", S.BILLS_PAYMENT, seconds=2))

    assert LongestQueueStrategy().select(queues) is S.BILLS_PAYMENT


def test_tie_goes_to_queue_with_oldest_head_ticket(make_ticket):
    queues = empty_queues()
    queues[S.BOXES].enqueue(make_ticket("X001", S.BOXES, seconds=10))
    queues[S.ACCOUNT_MANAGEMENT].enqueue(make_ticket("A001", S.ACCOUNT_MANAGEMENT, seconds=5))

    assert LongestQueueStrategy().select(queues) is S.ACCOUNT_MANAGEMENT


def test_only_considers_queues_it_is_given(make_ticket):
    queues = empty_queues()
    queues[S.BOXES].enqueue(make_ticket("X001", S.BOXES))
    queues[S.BOXES].enqueue(make_ticket("X002", S.BOXES, seconds=1))
    queues[S.BILLS_PAYMENT].enqueue(make_ticket("B001", S.BILLS_PAYMENT, seconds=2))
    del queues[S.BOXES]

    assert LongestQueueStrategy().select(queues) is S.BILLS_PAYMENT
