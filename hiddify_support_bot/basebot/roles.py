from enum import Enum


class Role(Enum):
    SUPER_ADMIN = "super_admin"
    SUPPORT = "support"
    USER = "user"
    UNKNOWN="unknown"

