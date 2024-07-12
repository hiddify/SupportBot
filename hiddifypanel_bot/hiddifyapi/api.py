from __future__ import annotations
import os
import aiohttp
from datetime import datetime
import uuid
import qrcode
from io import BytesIO
from typing import Optional, Dict, List, Union, TypedDict
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer
from .schemas import *

class HiddifyApiError(Exception):
    """Custom exception for HiddifyApi errors."""

HIDDIFYPANEL_USER_LINK = os.getenv("HIDDIFYPANEL_USER_LINK").rstrip("/")
HIDDIFYPANEL_ADMIN_LINK = os.getenv("HIDDIFYPANEL_ADMIN_LINK").rstrip("/")

class HiddifyApi:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None

    

    
    def get_admin_link(self):
        return f"{HIDDIFYPANEL_ADMIN_LINK}/{self.api_key}/"

    def get_user_link(self):
        return f"{HIDDIFYPANEL_USER_LINK}/{self.api_key}/"

    async def _make_request(self, method: str, endpoint: str, api_key=None, admin=True, **kwargs) -> dict:
        """Make an asynchronous HTTP request to the API."""
        if admin:
            url = f"{HIDDIFYPANEL_ADMIN_LINK}/{endpoint.strip('/')}/"
        else:
            url = f"{HIDDIFYPANEL_USER_LINK}/{endpoint.strip('/')}/"
        
        headers = {"HIDDIFY-API-KEY": api_key or self.api_key}
        
        try:
            session=aiohttp.ClientSession()
            async with session:
             async with session.request(method, url, headers=headers, ssl=False, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            raise HiddifyApiError(f"Error in API request: {e}") from e

    async def get_system_status(self) -> SystemStatus:
        """Get the system status."""
        data = await self._make_request("GET", "api/v2/admin/server_status/")
        return SystemStatus(stats=data.get("stats", {}), usage_history=data.get("usage_history", {}))

    async def get_admin_list(self) -> List[Dict[str, Union[str, int]]]:
        """Get the list of admin users."""
        return await self._make_request("GET", "api/v2/admin/admin_user/")

    async def delete_admin_user(self, uuid: str) -> bool:
        """Delete an admin user."""
        await self._make_request("DELETE", f"api/v2/admin/admin_user/{uuid}/")
        return True

    async def add_user(self, user: User) -> User:
        return await self._make_request("POST", "api/v2/admin/user/", json=user)

    async def get_user_info(self, uuid: str = None) -> UserInfo:
        """Get detailed user information."""
        response = await self._make_request("GET", f"api/v2/user/me", api_key=uuid, admin=False)
        return UserInfo(**response)

    async def update_my_user(self, data: User):
        return await self._make_request("PATCH", f"api/v2/user/", json=data, admin=False)

    async def get_admin_info(self, uuid: str = None) -> AdminInfo:
        """Get detailed user information."""
        response = await self._make_request("GET", f"api/v2/admin/me", api_key=uuid)
        return UserInfo(**response)

    async def get_user_list(self) -> List[User]:
        """Get the list of users."""
        return await self._make_request("GET", "api/v2/admin/user/")

    async def get_user_list_by_name(self, query_name: str, offset: int, count: int) -> List[User]:
        """Get the list of users filtered by name."""
        users = await self.get_user_list()
        lis = [user for user in users if query_name.lower() in user.get("name", "").lower()]

        if len(lis) < offset:
            return []
        return lis[offset : offset + count]

    async def update_user(self, uuid: str, data: User) -> User:
        """Update user information."""
        return await self._make_request("PATCH", f"api/v2/admin/user/{uuid}/", json=data)

    async def reset_user_last_reset_time(self, uuid: str) -> User:
        """Reset the user's last reset time."""
        user_data = await self.find_user(uuid)
        if not user_data:
            raise HiddifyApiError("User not found.")
        user_data |= {"last_reset_time": datetime.now().strftime("%Y-%m-%d"), "start_date": None, "current_usage_GB": 0}
        return await self.update_user(uuid, user_data)

    async def reset_package_days(self, uuid: str) -> User:
        """Update the package days for a user."""
        user_data = await self.get_user(uuid)
        if not user_data:
            raise HiddifyApiError("User not found.")
        user_data |= {"last_reset_time": datetime.now().strftime("%Y-%m-%d"), "start_date": None}
        return await self.update_user(uuid, user_data)

    async def reset_traffic(self, uuid: str) -> User:
        """Reset the traffic limit for a user to 0."""
        user_data = await self.get_user(uuid)
        if not user_data:
            raise HiddifyApiError("User not found.")
        user_data["current_usage_GB"] = 0
        return await self.update_user(uuid, user_data)

    async def delete_user(self, uuid: str) -> bool:
        """Delete a user."""
        await self._make_request("DELETE", f"api/v2/admin/user/{uuid}/")
        return True

    async def get_user(self, uuid: str) -> User:
        """Find a user by UUID."""
        return await self._make_request("GET", f"api/v2/admin/user/{uuid}/")

    async def backup_file(self) -> bytes:
        """Backup the file."""
        response = await self._make_request("GET", "admin/backup/backupfile/")
        return response

    async def get_app_information(self, uuid: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Get information about available apps for a given UUID."""
        params = {"platform": "all"}
        return await self._make_request("GET", "api/v2/user/apps/", params=params, api_key=uuid, admin=False)

    @staticmethod
    def generate_qr_code(data: str) -> BytesIO:
        """Generate a QR code for the given data."""
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_byte_io = BytesIO()
        qr_img.save(qr_byte_io, format="PNG")
        qr_byte_io.seek(0)
        return qr_byte_io