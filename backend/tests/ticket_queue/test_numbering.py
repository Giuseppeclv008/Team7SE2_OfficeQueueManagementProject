import pytest

from app.ticket_queue import DailyServiceNumberGenerator, ServiceType, format_code

S = ServiceType


@pytest.fixture
def generator(fake_today):
    return DailyServiceNumberGenerator(today=fake_today)


def test_first_code_is_one_for_every_service(generator):
    assert [generator.next(s) for s in ServiceType] == [1, 1, 1]


def test_codes_increment_per_service(generator):
    assert [generator.next(S.BOXES) for _ in range(3)] == [1, 2, 3]


def test_each_service_has_its_own_counter(generator):
    generator.next(S.BOXES)
    generator.next(S.BOXES)

    assert generator.next(S.BILLS_PAYMENT) == 1
    assert generator.next(S.BOXES) == 3


def test_counters_reset_on_a_new_day(generator, fake_today):
    generator.next(S.BOXES)
    generator.next(S.BOXES)
    generator.next(S.ACCOUNT_MANAGEMENT)

    fake_today.advance()

    assert generator.next(S.BOXES) == 1
    assert generator.next(S.ACCOUNT_MANAGEMENT) == 1


def test_counters_do_not_reset_within_the_same_day(generator):
    generator.next(S.BOXES)

    assert generator.next(S.BOXES) == 2


@pytest.mark.parametrize(
    ("service", "code", "expected"),
    [
        (S.BOXES, 1, "X001"),
        (S.BILLS_PAYMENT, 42, "B042"),
        (S.ACCOUNT_MANAGEMENT, 999, "A999"),
    ],
)
def test_format_code_uses_service_prefix_and_padding(service, code, expected):
    assert format_code(service, code) == expected


def test_format_code_above_999_grows_instead_of_wrapping():
    assert format_code(S.BOXES, 1000) == "X1000"


def test_format_code_custom_prefixes_and_digits():
    assert format_code(S.BOXES, 1, prefixes={S.BOXES: "Z"}, digits=2) == "Z01"


def test_numbering_resumes_from_last_stored_code(fake_today):
    stored = {S.BOXES: 4}
    generator = DailyServiceNumberGenerator(
        today=fake_today, last_code=lambda service, day: stored.get(service, 0)
    )

    assert [generator.next(S.BOXES) for _ in range(2)] == [5, 6]
    assert generator.next(S.BILLS_PAYMENT) == 1


def test_last_code_is_looked_up_once_per_service_per_day(fake_today):
    calls = []

    def last_code(service, day):
        calls.append((service, day))
        return 0

    generator = DailyServiceNumberGenerator(today=fake_today, last_code=last_code)
    generator.next(S.BOXES)
    generator.next(S.BOXES)
    fake_today.advance()
    generator.next(S.BOXES)

    assert len(calls) == 2
    assert calls[0][1] != calls[1][1]
