from collections.abc import Mapping

from .interfaces import SelectionStrategy, TicketQueue
from .models import ServiceType


class LongestQueueStrategy(SelectionStrategy):
    """Serve the longest queue; on a tie, the queue whose head ticket is oldest."""

    def select(self, queues: Mapping[ServiceType, TicketQueue]) -> ServiceType | None:
        candidates = [(service, queue) for service, queue in queues.items() if len(queue) > 0]
        if not candidates:
            return None
        service, _ = min(
            candidates,
            key=lambda item: (-len(item[1]), item[1].peek().issued_at),
        )
        return service
