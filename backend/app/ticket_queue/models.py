"""Domain types for the ticket queue.

ServiceType is the shared enum from app.models, re-exported here so the
rest of the package keeps importing it from .models.
"""
from dataclasses import dataclass
from datetime import datetime

from app.models.serviceType import ServiceType

__all__ = ["ServiceType", "Ticket"]


@dataclass(frozen=True)
class Ticket:
    number: str  # e.g. "X001"
    service: ServiceType
    issued_at: datetime
