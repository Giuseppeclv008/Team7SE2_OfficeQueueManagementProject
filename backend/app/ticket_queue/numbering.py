from collections.abc import Callable, Mapping
from datetime import date

from .interfaces import TicketNumberGenerator
from .models import ServiceType

DEFAULT_PREFIXES: Mapping[ServiceType, str] = {
    ServiceType.BOXES: "X",
    ServiceType.BILLS_PAYMENT: "B",
    ServiceType.ACCOUNT_MANAGEMENT: "A",
}


class DailyServiceNumberGenerator(TicketNumberGenerator):
    """Numbers like "X001": service prefix + per-service counter.

    Every counter restarts from 1 on the first ticket of a new day.
    Not locked on its own: QueueManager calls it while holding its lock.
    """

    def __init__(
        self,
        prefixes: Mapping[ServiceType, str] = DEFAULT_PREFIXES,
        today: Callable[[], date] = date.today,
        digits: int = 3,
    ) -> None:
        self._prefixes = dict(prefixes)
        self._today = today
        self._digits = digits
        self._day: date | None = None
        self._counters: dict[ServiceType, int] = {}

    def next(self, service: ServiceType) -> str:
        today = self._today()
        if today != self._day:
            self._day = today
            self._counters.clear()
        self._counters[service] = self._counters.get(service, 0) + 1
        return f"{self._prefixes[service]}{self._counters[service]:0{self._digits}d}"
