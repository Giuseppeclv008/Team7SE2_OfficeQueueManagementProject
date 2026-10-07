import pytest

from ticket_queue import DailyServiceNumberGenerator, ServiceType

S = ServiceType


@pytest.fixture
def generator(fake_today):
    return DailyServiceNumberGenerator(today=fake_today)


@pytest.mark.parametrize(
    ("service", "expected"),
    [(S.BOXES, "X001"), (S.BILLS_PAYMENT, "B001"), (S.ACCOUNT_MANAGEMENT, "A001")],
)
def test_first_number_uses_service_prefix(generator, service, expected):
    assert generator.next(service) == expected


def test_numbers_increment_per_service(generator):
    assert [generator.next(S.BOXES) for _ in range(3)] == ["X001", "X002", "X003"]


def test_each_service_has_its_own_counter(generator):
    generator.next(S.BOXES)
    generator.next(S.BOXES)

    assert generator.next(S.BILLS_PAYMENT) == "B001"
    assert generator.next(S.BOXES) == "X003"


def test_counters_reset_on_a_new_day(generator, fake_today):
    generator.next(S.BOXES)
    generator.next(S.BOXES)
    generator.next(S.ACCOUNT_MANAGEMENT)

    fake_today.advance()

    assert generator.next(S.BOXES) == "X001"
    assert generator.next(S.ACCOUNT_MANAGEMENT) == "A001"


def test_counters_do_not_reset_within_the_same_day(generator):
    generator.next(S.BOXES)

    assert generator.next(S.BOXES) == "X002"


def test_numbers_above_999_grow_instead_of_wrapping(fake_today):
    generator = DailyServiceNumberGenerator(today=fake_today)
    for _ in range(999):
        generator.next(S.BOXES)

    assert generator.next(S.BOXES) == "X1000"


def test_custom_prefixes_and_digits(fake_today):
    generator = DailyServiceNumberGenerator(
        prefixes={S.BOXES: "Z"}, today=fake_today, digits=2
    )

    assert generator.next(S.BOXES) == "Z01"
