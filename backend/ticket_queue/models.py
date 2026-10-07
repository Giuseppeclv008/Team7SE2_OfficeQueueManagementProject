"""Domain types for the ticket queue.

ServiceType has no queue-specific dependencies so it can be moved to a
shared module if other parts of the system need it.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ServiceType(Enum):
    BOXES = "boxes"
    BILLS_PAYMENT = "bills_payment"
    ACCOUNT_MANAGEMENT = "account_management"


@dataclass(frozen=True)
class Ticket:
    number: str  # e.g. "X001"
    service: ServiceType
    issued_at: datetime
