import enum

from sqlalchemy import Enum

class TicketStatus(enum.Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"