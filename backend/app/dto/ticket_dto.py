from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.serviceType import ServiceType
from app.models.ticketStatus import TicketStatus


class ServiceListDTO(BaseModel):
    services: list[ServiceType]


class TicketCreateDTO(BaseModel):
    service_type: ServiceType


class TicketResponseDTO(BaseModel):
    id: UUID
    code: int
    service_type: ServiceType
    status: TicketStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)