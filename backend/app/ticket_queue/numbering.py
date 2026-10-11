from collections.abc import Callable, Mapping
from datetime import date

from .interfaces import TicketNumberGenerator
from .models import ServiceType

DEFAULT_PREFIXES: Mapping[ServiceType, str] = {
    ServiceType.BOXES: "X",
    ServiceType.BILLS_PAYMENT: "B",
    ServiceType.ACCOUNT_MANAGEMENT: "A",
}


def format_code(
    service: ServiceType,
    code: int,
    prefixes: Mapping[ServiceType, str] = DEFAULT_PREFIXES,
    digits: int = 3,
) -> str:
    """Display form of a ticket code, e.g. (BOXES, 1) -> "X001"."""
    return f"{prefixes[service]}{code:0{digits}d}"


LastCodeLookup = Callable[[ServiceType, date], int]


def _no_previous_codes(service: ServiceType, day: date) -> int:
    return 0


class DailyServiceNumberGenerator(TicketNumberGenerator):
    """Per-service counter that restarts from 1 on the first ticket of a new day.

    last_code returns the highest code already issued for a service on a day
    (0 if none). It is called once per service per day, so after a restart
    numbering resumes from the stored tickets instead of starting again at 1.

    Not locked on its own: QueueManager calls it while holding its lock.
    """

    def __init__(
        self,
        today: Callable[[], date] = date.today,
        last_code: LastCodeLookup = _no_previous_codes,
    ) -> None:
        self._today = today
        self._last_code = last_code
        self._day: date | None = None
        self._counters: dict[ServiceType, int] = {}

    def next(self, service: ServiceType) -> int:
        today = self._today()
        if today != self._day:
            self._day = today
            self._counters.clear()
        if service not in self._counters:
            self._counters[service] = self._last_code(service, today)
        self._counters[service] += 1
        return self._counters[service]
