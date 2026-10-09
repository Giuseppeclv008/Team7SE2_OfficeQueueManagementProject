import pytest

from app.dao.customer_dao import CustomerDAO
from app.dto.auth_mockup_dto import CustomerDTO, UserRole


# --- seed data --------------------------------------------------------------


def test_starts_with_one_mock_customer():
    customers = CustomerDAO().find_all()

    assert customers == [CustomerDTO(id=1, name="Customer 1", role=UserRole.CUSTOMER)]


def test_instances_do_not_share_state():
    first = CustomerDAO()
    first.save(CustomerDTO(id=2, name="Alice"))

    assert CustomerDAO().find_by_id(2) is None


# --- find_by_id -------------------------------------------------------------


def test_find_by_id_returns_customer():
    customer = CustomerDAO().find_by_id(1)

    assert customer is not None
    assert customer.id == 1
    assert customer.role is UserRole.CUSTOMER


def test_find_by_id_returns_none_for_unknown_id():
    assert CustomerDAO().find_by_id(999) is None


# --- save -------------------------------------------------------------------


def test_save_adds_new_customer():
    dao = CustomerDAO()
    alice = CustomerDTO(id=2, name="Alice")

    dao.save(alice)

    assert dao.find_by_id(2) == alice
    assert len(dao.find_all()) == 2


def test_save_overwrites_customer_with_same_id():
    dao = CustomerDAO()

    dao.save(CustomerDTO(id=1, name="Renamed"))

    assert dao.find_by_id(1).name == "Renamed"
    assert len(dao.find_all()) == 1


# --- find_all ---------------------------------------------------------------


def test_find_all_returns_a_copy():
    dao = CustomerDAO()

    dao.find_all().clear()

    assert len(dao.find_all()) == 1


def test_find_all_keeps_insertion_order():
    dao = CustomerDAO()
    dao.save(CustomerDTO(id=3, name="C"))
    dao.save(CustomerDTO(id=2, name="B"))

    assert [c.id for c in dao.find_all()] == [1, 3, 2]


# --- known bugs (code review) -----------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="Storage is per instance and re-seeded in __init__, so a customer "
    "saved through one DAO (e.g. one request) is gone in the next.",
)
def test_bug_saved_customer_lost_with_new_dao_instance():
    customer = CustomerDTO(id=42, name="Mario")
    CustomerDAO().save(customer)

    assert CustomerDAO().find_by_id(42) == customer
