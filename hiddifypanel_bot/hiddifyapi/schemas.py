
from typing import TypedDict, Optional, Literal,Dict,Union,List

class UserInfo(TypedDict):
    admin_message_html: str
    admin_message_url: str
    brand_icon_url: str
    brand_title: str
    doh: str
    lang: str
    profile_remaining_days: int
    profile_reset_days: int
    profile_title: str
    profile_url: str
    profile_usage_current: float
    profile_usage_total: float
    speedtest_enable: bool
    telegram_bot_url: str
    telegram_id: Optional[int]
    telegram_proxy_enable: bool





class AdminInfo(TypedDict):
    can_add_admin: bool
    comment: str
    lang: str
    max_active_users: int
    max_users: int
    mode: Literal['super_admin', 'admin', 'agent']  # Assuming these are the possible modes
    name: str
    parent_admin_uuid: Optional[str]
    telegram_id: int
    uuid: Optional[str]


class User(TypedDict):
    comment: str
    current_usage_GB: float
    mode: str
    name: str
    package_days: int
    telegram_id: int
    usage_limit_GB: float
    uuid: str
    enable:bool

class SystemStatus(TypedDict):
    stats: Dict[str, Union[int, float, str]]
    usage_history: Dict[str, List[Union[int, float]]]
