from enum import Enum
from typing import Literal
from pydantic import BaseModel


class UserRole(str, Enum):
    CUSTOMER = "customer"
    OFFICER = "officer"


class CustomerDTO(BaseModel):
    id: int
    name: str
    role: Literal[UserRole.CUSTOMER] = UserRole.CUSTOMER


class OfficerDTO(BaseModel):
    id: int
    name: str
    counter_id: str
    role: Literal[UserRole.OFFICER] = UserRole.OFFICER