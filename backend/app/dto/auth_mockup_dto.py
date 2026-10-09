from enum import Enum
from pydantic import BaseModel
from typing import Literal


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
    counter_id: int
    role: Literal[UserRole.OFFICER] = UserRole.OFFICER