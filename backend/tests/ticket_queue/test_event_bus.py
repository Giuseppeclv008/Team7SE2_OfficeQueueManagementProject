import logging

from app.ticket_queue import InMemoryEventBus


class Ping:
    pass


class Pong:
    pass


def test_publish_delivers_to_subscribers_of_that_event_type():
    bus = InMemoryEventBus()
    received = []
    bus.subscribe(Ping, received.append)
    event = Ping()

    bus.publish(event)

    assert received == [event]


def test_publish_ignores_subscribers_of_other_event_types():
    bus = InMemoryEventBus()
    received = []
    bus.subscribe(Pong, received.append)

    bus.publish(Ping())

    assert received == []


def test_publish_without_subscribers_does_nothing():
    InMemoryEventBus().publish(Ping())


def test_handlers_are_called_in_subscription_order():
    bus = InMemoryEventBus()
    calls = []
    bus.subscribe(Ping, lambda e: calls.append("first"))
    bus.subscribe(Ping, lambda e: calls.append("second"))

    bus.publish(Ping())

    assert calls == ["first", "second"]


def test_unsubscribed_handler_is_no_longer_called():
    bus = InMemoryEventBus()
    received = []
    bus.subscribe(Ping, received.append)
    bus.unsubscribe(Ping, received.append)

    bus.publish(Ping())

    assert received == []


def test_unsubscribing_unknown_handler_is_ignored():
    bus = InMemoryEventBus()

    bus.unsubscribe(Ping, print)


def test_failing_handler_is_logged_and_others_still_run(caplog):
    bus = InMemoryEventBus()
    received = []

    def failing(event):
        raise RuntimeError("boom")

    bus.subscribe(Ping, failing)
    bus.subscribe(Ping, received.append)

    with caplog.at_level(logging.ERROR):
        bus.publish(Ping())

    assert len(received) == 1
    assert "boom" in caplog.text


def test_handler_can_unsubscribe_itself_during_delivery():
    bus = InMemoryEventBus()
    calls = []

    def once(event):
        calls.append("once")
        bus.unsubscribe(Ping, once)

    bus.subscribe(Ping, once)
    bus.subscribe(Ping, lambda e: calls.append("other"))

    bus.publish(Ping())
    bus.publish(Ping())

    assert calls == ["once", "other", "other"]
