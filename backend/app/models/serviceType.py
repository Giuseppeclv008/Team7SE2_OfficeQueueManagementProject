import enum

from sqlalchemy import Enum


class ServiceType(enum.Enum):
    BOXES = "boxes"
    BILLS_PAYMENT = "bills_payment"
    ACCOUNT_MANAGEMENT = "account_management"