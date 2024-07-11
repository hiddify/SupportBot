from __future__ import annotations

import requests
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

class HiddifyApi:
    def __init__(self, api_url: str, api_key: str):
        self.base_url: str = api_url.rstrip('/')
        
        self.api_key=api_key
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


    def _make_request(self, method: str, endpoint: str,api_key=None, **kwargs) -> requests.Response:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint.strip('/')}/"
        try:
            response = requests.request(method, url, headers={'HIDDIFY-API-KEY': api_key or self.api_key},verify=False, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise HiddifyApiError(f"Error in API request: {e}") from e

    def get_system_status(self) -> SystemStatus:
        """Get the system status."""
        response = self._make_request("GET", "api/v2/admin/server_status/")
        data = response.json()
        return SystemStatus(
            stats=data.get("stats", {}),
            usage_history=data.get("usage_history", {})
        )

    def get_admin_list(self) -> List[Dict[str, Union[str, int]]]:
        """Get the list of admin users."""
        response = self._make_request("GET", "api/v2/admin/admin_user/")
        return response.json()

    def delete_admin_user(self, uuid: str) -> bool:
        """Delete an admin user."""
        self._make_request("DELETE", f"api/v2/admin/admin_user/{uuid}/")
        return True

    def add_user(self, user:User)->User:
        return self._make_request("POST", "api/v2/admin/user/", json=user)

    
    def get_user_info(self,uuid:str=None) -> UserInfo:
        """Get detailed user information."""
        response = self._make_request("GET", f"api/v2/user/me",api_key=uuid)
        return UserInfo(**response.json())
    def update_my_user(self,data:User):
        return self._make_request("PATCH", f"api/v2/user/", json=data)
    def get_admin_info(self,uuid:str=None) -> AdminInfo:
        """Get detailed user information."""
        response = self._make_request("GET", f"api/v2/admin/me",api_key=uuid)
        return UserInfo(**response.json())

    def get_user_list(self) -> List[User]:
        """Get the list of users."""
        response = self._make_request("GET", "api/v2/admin/user/")
        return response.json()

    def get_user_list_by_name(self, query_name: str, offset:int, count:int) -> List[User]:
        """Get the list of users filtered by name."""
        users = self.get_user_list()
        lis= [user for user in users if query_name.lower() in user.get('name', '').lower()]
        
        if len(lis)<offset:
            return []
        return lis[offset:offset+count]


    def update_user(self, uuid: str, data: User) -> User:
        """Update user information."""
        return self._make_request("PATCH", f"api/v2/admin/user/{uuid}/", json=data)

    def reset_user_last_reset_time(self, uuid: str) -> User:
        """Reset the user's last reset time."""
        user_data = self.find_user(uuid)
        if not user_data:
            raise HiddifyApiError("User not found.")
        user_data |= {
            'last_reset_time': datetime.now().strftime('%Y-%m-%d'),
            'start_date': None,
            'current_usage_GB': 0
        }
        return self.update_user(uuid, user_data)

    def reset_package_days(self, uuid: str) -> User:
        """Update the package days for a user."""
        user_data = self.find_user(uuid)
        if not user_data:
            raise HiddifyApiError("User not found.")
        user_data |= {
            'last_reset_time': datetime.now().strftime('%Y-%m-%d'),
            'start_date': None
        }
        return self.update_user(uuid, user_data)

    def reset_traffic(self, uuid: str) -> User:
        """Reset the traffic limit for a user to 0."""
        user_data = self.find_user(uuid)
        if not user_data:
            raise HiddifyApiError("User not found.")
        user_data['current_usage_GB'] = 0
        return self.update_user(uuid, user_data)

    def delete_user(self, uuid: str) -> bool:
        """Delete a user."""
        self._make_request("DELETE", f"api/v2/admin/user/{uuid}/")
        return True

    def get_user(self, uuid: str) -> User:
        """Find a user by UUID."""
        response = self._make_request("GET", f"api/v2/admin/user/{uuid}/")
        return response.json()

    def backup_file(self) -> bytes:
        """Backup the file."""
        response = self._make_request("GET", "admin/backup/backupfile/")
        return response.content

    def get_app_information(self, uuid: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Get information about available apps for a given UUID."""
        url = f"{self.base_url}/api/v2/user/apps/"
        params = {"platform": "all"}
        response = self._make_request("GET", url, params=params,api_key=uuid)
        return response.json()

    @staticmethod
    def generate_qr_code(data: str) -> BytesIO:
        """Generate a QR code for the given data."""
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image(
            fill_color="White",
            back_color="Transparent",
            image_factory=StyledPilImage,
            module_drawer=CircleModuleDrawer(),
            color_mask=RadialGradiantColorMask()
        )
        
        qr_byte_io = BytesIO()
        qr_img.save(qr_byte_io, format='PNG')
        qr_byte_io.seek(0)
        
        return qr_byte_io