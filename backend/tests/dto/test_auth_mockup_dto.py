import pytest
from pydantic import ValidationError

from app.dto.auth_mockup_dto import CustomerDTO, OfficerDTO, UserRole


# --- UserRole ---------------------------------------------------------------


def test_user_role_values():
    assert UserRole.CUSTOMER == "customer"
    assert UserRole.OFFICER == "officer"
    assert UserRole("officer") is UserRole.OFFICER


# --- CustomerDTO ------------------------------------------------------------


def test_customer_role_defaults_to_customer():
    assert CustomerDTO(id=1, name="Alice").role is UserRole.CUSTOMER


def test_customer_accepts_role_as_string():
    assert CustomerDTO.model_validate({"id": 1, "name": "A", "role": "customer"}).role is UserRole.CUSTOMER


@pytest.mark.parametrize("missing", ["id", "name"])
def test_customer_requires_field(missing):
    data = {"id": 1, "name": "Alice"}
    del data[missing]

    with pytest.raises(ValidationError):
        CustomerDTO.model_validate(data)


@pytest.mark.parametrize("bad_role", ["admin", "", None])
def test_customer_rejects_unknown_role(bad_role):
    with pytest.raises(ValidationError):
        CustomerDTO.model_validate({"id": 1, "name": "A", "role": bad_role})


def test_customer_rejects_non_integer_id():
    with pytest.raises(ValidationError):
        CustomerDTO.model_validate({"id": "abc", "name": "A"})


def test_customer_serializes_role_as_value():
    assert CustomerDTO(id=1, name="A").model_dump(mode="json") == {
        "id": 1,
        "name": "A",
        "role": "customer",
    }


# --- OfficerDTO -------------------------------------------------------------


def test_officer_role_defaults_to_officer():
    assert OfficerDTO(id=1, name="Bob", counter_id=1).role is UserRole.OFFICER


@pytest.mark.parametrize("missing", ["id", "name", "counter_id"])
def test_officer_requires_field(missing):
    data = {"id": 1, "name": "Bob", "counter_id": 1}
    del data[missing]

    with pytest.raises(ValidationError):
        OfficerDTO.model_validate(data)


def test_officer_rejects_non_integer_counter_id():
    with pytest.raises(ValidationError):
        OfficerDTO.model_validate({"id": 1, "name": "Bob", "counter_id": "front"})


def test_officer_serializes_role_as_value():
    assert OfficerDTO(id=1, name="Bob", counter_id=2).model_dump(mode="json") == {
        "id": 1,
        "name": "Bob",
        "counter_id": 2,
        "role": "officer",
    }
