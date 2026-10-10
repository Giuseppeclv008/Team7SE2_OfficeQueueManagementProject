from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    CUSTOMER = "customer"
    OFFICER = "officer"


class CustomerDTO(BaseModel):
    id: int
    name: str
    role: UserRole = UserRole.CUSTOMER


class OfficerDTO(BaseModel):
    id: int
    name: str
    counter_id: int
    role: UserRole = UserRole.OFFICER