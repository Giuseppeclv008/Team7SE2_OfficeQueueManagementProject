"""Counter eligibility rules.

To restrict counters to some services later, add e.g. a
ConfiguredServicesPolicy(mapping: dict[str, set[ServiceType]]) that raises
UnknownCounterError for unmapped counters, and inject it in the factory.
"""
from .interfaces import CounterPolicy
from .models import ServiceType


class AllServicesPolicy(CounterPolicy):
    """Every counter can serve every service."""

    def eligible_services(self, counter_id: str) -> set[ServiceType]:
        return set(ServiceType)
