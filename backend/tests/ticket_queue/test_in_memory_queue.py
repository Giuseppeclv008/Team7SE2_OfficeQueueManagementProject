from ticket_queue import InMemoryTicketQueue, ServiceType


def test_new_queue_is_empty():
    queue = InMemoryTicketQueue()

    assert len(queue) == 0
    assert queue.peek() is None
    assert queue.dequeue() is None


def test_dequeue_returns_tickets_in_fifo_order(make_ticket):
    queue = InMemoryTicketQueue()
    first = make_ticket("X001", ServiceType.BOXES)
    second = make_ticket("X002", ServiceType.BOXES, seconds=1)
    queue.enqueue(first)
    queue.enqueue(second)

    assert queue.dequeue() is first
    assert queue.dequeue() is second
    assert queue.dequeue() is None


def test_peek_returns_head_without_removing_it(make_ticket):
    queue = InMemoryTicketQueue()
    ticket = make_ticket("X001", ServiceType.BOXES)
    queue.enqueue(ticket)

    assert queue.peek() is ticket
    assert len(queue) == 1


def test_len_tracks_enqueue_and_dequeue(make_ticket):
    queue = InMemoryTicketQueue()
    for i in range(3):
        queue.enqueue(make_ticket(f"X00{i + 1}", ServiceType.BOXES, seconds=i))
    queue.dequeue()

    assert len(queue) == 2
