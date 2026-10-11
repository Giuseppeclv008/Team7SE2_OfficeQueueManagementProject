from typing import ClassVar

from app.dto.auth_mockup_dto import CustomerDTO, UserRole


def _seed() -> dict[int, CustomerDTO]:
    return {1: CustomerDTO(id=1, name="Customer 1", role=UserRole.CUSTOMER)}


class CustomerDAO:

    # Shared by every instance, so a customer saved in one request is still there in the next.
    customers: ClassVar[dict[int, CustomerDTO]] = _seed()

    @classmethod
    def reset(cls) -> None:
        """Restore the mock seed data."""
        cls.customers = _seed()

    def find_by_id(self, customer_id: int) -> CustomerDTO | None:
        return self.customers.get(customer_id)

    def find_all(self) -> list[CustomerDTO]:
        return list(self.customers.values())

    def save(self, customer: CustomerDTO) -> None:
        self.customers[customer.id] = customer
