from typing import ClassVar

from app.dto.auth_mockup_dto import OfficerDTO, UserRole


def _seed() -> dict[int, OfficerDTO]:
    return {
        1: OfficerDTO(id=1, name="Officer 1", counter_id=1, role=UserRole.OFFICER),
        2: OfficerDTO(id=2, name="Officer 2", counter_id=2, role=UserRole.OFFICER),
    }


class OfficerDAO:

    # Shared by every instance, so an officer saved in one request is still there in the next.
    officers: ClassVar[dict[int, OfficerDTO]] = _seed()

    @classmethod
    def reset(cls) -> None:
        """Restore the mock seed data."""
        cls.officers = _seed()

    def find_by_id(self, officer_id: int) -> OfficerDTO | None:
        return self.officers.get(officer_id)

    def find_all(self) -> list[OfficerDTO]:
        return list(self.officers.values())

    def save(self, officer: OfficerDTO) -> None:
        self.officers[officer.id] = officer
