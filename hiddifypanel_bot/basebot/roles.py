from enum import Enum


class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    AGENT = "agent"
    USER = "user"
    UNKNOWN="unknown"

