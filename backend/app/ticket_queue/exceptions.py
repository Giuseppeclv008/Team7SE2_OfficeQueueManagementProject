class QueueError(Exception):
    """Base class for ticket queue errors."""


class UnknownCounterError(QueueError):
    """Raised by a CounterPolicy for a counter it has no configuration for."""
