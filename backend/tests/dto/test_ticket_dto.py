import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.dto.services import SERVICES_LIST
from app.dto.ticket_dto import ServiceListDTO, TicketCreateDTO, TicketResponseDTO
from app.models import ServiceType, Ticket, TicketStatus
from app.ticket_queue import create_default_queue_manager

S = ServiceType


# --- TicketCreateDTO (request body of "get ticket") -------------------------


@pytest.mark.parametrize("service", list(ServiceType))
def test_create_dto_accepts_every_service_value(service):
    dto = TicketCreateDTO.model_validate({"service_type": service.value})

    assert dto.service_type is service


def test_create_dto_accepts_enum_member():
    assert TicketCreateDTO(service_type=S.BOXES).service_type is S.BOXES


@pytest.mark.parametrize("bad", ["coffee", "", "BOXES", 1, None])
def test_create_dto_rejects_unknown_service(bad):
    with pytest.raises(ValidationError):
        TicketCreateDTO.model_validate({"service_type": bad})


def test_create_dto_requires_service_type():
    with pytest.raises(ValidationError):
        TicketCreateDTO.model_validate({})


# --- TicketResponseDTO (response of "get ticket") ---------------------------


def test_response_dto_from_orm_ticket():
    ticket = Ticket(
        id=uuid.uuid4(),
        code=5,
        service_type=S.BILLS_PAYMENT,
        status=TicketStatus.WAITING,
        created_at=datetime(2026, 10, 7, 9, 0),
    )

    dto = TicketResponseDTO.model_validate(ticket)

    assert dto.id == ticket.id
    assert dto.code == 5
    assert dto.service_type is S.BILLS_PAYMENT
    assert dto.status is TicketStatus.WAITING
    assert dto.created_at == ticket.created_at


def test_response_dto_from_queue_ticket():
    issued = create_default_queue_manager().issue_ticket(S.BOXES)

    dto = TicketResponseDTO.model_validate(issued)

    assert dto.id == issued.id
    assert dto.code == 1
    assert dto.service_type is S.BOXES
    assert dto.status is TicketStatus.WAITING


def test_response_dto_serializes_enums_as_values():
    ticket_id = uuid.uuid4()
    dto = TicketResponseDTO(
        id=ticket_id,
        code=1,
        service_type=S.ACCOUNT_MANAGEMENT,
        status=TicketStatus.WAITING,
        created_at=datetime(2026, 10, 7, 9, 0, tzinfo=timezone.utc),
    )

    data = dto.model_dump(mode="json")

    assert data == {
        "id": str(ticket_id),
        "code": 1,
        "service_type": "account_management",
        "status": "waiting",
        "created_at": "2026-10-07T09:00:00Z",
    }


@pytest.mark.parametrize("missing", ["id", "code", "service_type", "status", "created_at"])
def test_response_dto_requires_every_field(missing):
    data = {
        "id": str(uuid.uuid4()),
        "code": 1,
        "service_type": "boxes",
        "status": "waiting",
        "created_at": "2026-10-07T09:00:00",
    }
    del data[missing]

    with pytest.raises(ValidationError):
        TicketResponseDTO.model_validate(data)


def test_response_dto_rejects_non_integer_code():
    with pytest.raises(ValidationError):
        TicketResponseDTO.model_validate(
            {
                "id": str(uuid.uuid4()),
                "code": "X001",
                "service_type": "boxes",
                "status": "waiting",
                "created_at": "2026-10-07T09:00:00",
            }
        )


# --- ServiceListDTO (services shown on the "get ticket" screen) -------------


def test_services_list_contains_every_service_once():
    assert sorted(SERVICES_LIST, key=lambda s: s.value) == sorted(ServiceType, key=lambda s: s.value)
    assert len(SERVICES_LIST) == len(set(SERVICES_LIST))


def test_service_list_dto_serializes_values():
    dto = ServiceListDTO(services=SERVICES_LIST)

    assert dto.model_dump(mode="json") == {
        "services": ["boxes", "bills_payment", "account_management"]
    }
