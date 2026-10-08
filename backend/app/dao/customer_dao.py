from app.dto.auth_mockup_dto import CustomerDTO, UserRole


class CustomerDAO:
    _customers: dict[int, CustomerDTO] = {
        1: CustomerDTO(id=1, name="Customer 1", role=UserRole.CUSTOMER)
    }

    def __init__(self):
        self.customers = self._customers

    def find_by_id(self, customer_id: int) -> CustomerDTO | None:
        return self.customers.get(customer_id)

    def find_all(self) -> list[CustomerDTO]:
        return list(self.customers.values())

    def save(self, customer: CustomerDTO) -> None:
        self.customers[customer.id] = customer