from app.dao.officer_dao import OfficerDAO
from app.dto.auth_mockup_dto import OfficerDTO, UserRole


# --- seed data --------------------------------------------------------------


def test_starts_with_two_mock_officers_on_distinct_counters():
    officers = OfficerDAO().find_all()

    assert [(o.id, o.counter_id) for o in officers] == [(1, 1), (2, 2)]
    assert all(o.role is UserRole.OFFICER for o in officers)


def test_instances_do_not_share_state():
    OfficerDAO().save(OfficerDTO(id=3, name="Bob", counter_id=3))

    assert OfficerDAO().find_by_id(3) is None


# --- find_by_id -------------------------------------------------------------


def test_find_by_id_returns_officer():
    officer = OfficerDAO().find_by_id(2)

    assert officer == OfficerDTO(id=2, name="Officer 2", counter_id=2)


def test_find_by_id_returns_none_for_unknown_id():
    assert OfficerDAO().find_by_id(999) is None


# --- save -------------------------------------------------------------------


def test_save_adds_new_officer():
    dao = OfficerDAO()
    bob = OfficerDTO(id=3, name="Bob", counter_id=3)

    dao.save(bob)

    assert dao.find_by_id(3) == bob
    assert len(dao.find_all()) == 3


def test_save_overwrites_officer_with_same_id():
    dao = OfficerDAO()

    dao.save(OfficerDTO(id=1, name="Officer 1", counter_id=5))

    assert dao.find_by_id(1).counter_id == 5
    assert len(dao.find_all()) == 2


# --- find_all ---------------------------------------------------------------


def test_find_all_returns_a_copy():
    dao = OfficerDAO()

    dao.find_all().clear()

    assert len(dao.find_all()) == 2
