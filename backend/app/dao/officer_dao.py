from app.dto.auth_mockup_dto import OfficerDTO, UserRole


class OfficerDAO:
    _officers: dict[int, OfficerDTO] = {
        1: OfficerDTO(
            id=1, name="Officer 1", counter_id="1", role=UserRole.OFFICER
        ),
        2: OfficerDTO(
            id=2, name="Officer 2", counter_id="2", role=UserRole.OFFICER
        ),
    }

    def __init__(self):
        self.officers = self._officers

    def find_by_id(self, officer_id: int) -> OfficerDTO | None:
        return self.officers.get(officer_id)

    def find_all(self) -> list[OfficerDTO]:
        return list(self.officers.values())

    def save(self, officer: OfficerDTO) -> None:
        self.officers[officer.id] = officer