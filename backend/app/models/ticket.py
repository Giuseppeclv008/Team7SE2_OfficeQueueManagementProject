from datetime import datetime
import uuid
import uuid

from sqlalchemy import Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid

from app.database import Base
from app.models.serviceType import ServiceType
from app.models.ticketStatus import TicketStatus


class Ticket(Base):

    __tablename__ = "ticket"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)    
    code: Mapped[int] = mapped_column(nullable=False)
    service_type: Mapped[ServiceType] = mapped_column( Enum(ServiceType),nullable=False)
    status: Mapped[TicketStatus] = mapped_column( Enum(TicketStatus), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())