# api.py

import uuid
from datetime import datetime
import qrcode
from io import BytesIO
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer
import aiohttp
import asyncio


class HiddifyApi:
    def __init__(self, api_url: str, api_key: str):
        self.base_url = api_url
        self.headers = {'HIDDIFY-API-KEY': api_key}


    async def get_system_status(self) -> dict:
        """Get the system status."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/v2/admin/server_status/", headers=self.headers) as response:
                    data = await response.json()
                    stats = data.get("stats", {})
                    usage_history = data.get("usage_history", {})
                    stats["usage_history"] = usage_history
                    return stats
            except aiohttp.ClientError as e:
                print(f"Error in get_system_status: {e}")
                return {}

    async def make_post_request(self, endpoint: str, json_data: dict) -> dict:
        """Make a POST request."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(endpoint, json=json_data, headers=self.headers) as response:
                    return response
            except aiohttp.ClientError as e:
                print(f"Error in making POST request: {e}")
                return False

    async def make_patch_request(self, endpoint: str, json_data: dict) -> dict:
        """Make a PATCH request."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(endpoint, json=json_data, headers=self.headers) as response:
                    return response
            except aiohttp.ClientError as e:
                print(f"Error in making PATCH request: {e}")
                return False

    async def get_admin_list(self) -> list:
        """Get the list of admin users."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/v2/admin/admin_user/", headers=self.headers) as response:
                    return await response.json()
            except aiohttp.ClientError as e:
                print(f"Error in get_admin_list: {e}")
                return []

    async def delete_admin_user(self, uuid: str) -> bool:
        """Delete an admin user."""
        async with aiohttp.ClientSession() as session:
            try:
                endpoint = f"{self.base_url}/api/v2/admin/admin_user/{uuid}/"
                async with session.delete(endpoint, headers=self.headers) as response:
                    return response.status == 200
            except aiohttp.ClientError as e:
                print(f"Error in delete_admin_user: {e}")
                return False

    async def add_service(self, comment: str, name: str, day: int, traffic: float, telegram_id: int=None,uuid: str=None) -> bool:
        """Add a new service."""
        data = {
            "comment": comment,
            "current_usage_GB": 0,
            "mode": "no_reset",
            "name": name,
            "package_days": day,
            "telegram_id": None,
            "usage_limit_GB": traffic,
            "uuid": uuid,
        }
        endpoint = f"{self.base_url}/api/v2/admin/user/"
        return await self.make_post_request(endpoint, data)

    async def get_user_list(self) -> list:
        """Get the list of users."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/v2/admin/user/", headers=self.headers) as response:
                    return await response.json()
            except aiohttp.ClientError as e:
                print(f"Error in get_user_list: {e}")
                return []

    async def get_user_list_name(self, query_name: str) -> list:
        """Get the list of users and filter by name containing the query."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/v2/admin/user/", headers=self.headers) as response:
                    user_list = await response.json()
                    filtered_users = [user for user in user_list if query_name.lower() in user.get('name', '').lower()]
                    return filtered_users
            except aiohttp.ClientError as e:
                print(f"Error in get_user_list_name: {e}")
                return []

    async def tele_id(self, uuid: str, telegram_id: int) -> bool:
        """Add Telegram ID."""
        data = {
            "telegram_id": telegram_id
        }
        endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
        return await self.make_patch_request(endpoint, data)

    async def reset_user_last_reset_time(self, uuid: str) -> bool:
        """Reset the user's last reset time."""
        user_data = await self.find_service(uuid)
        if not user_data:
            print("User not found.")
            return False
        user_data['last_reset_time'] = datetime.now().strftime('%Y-%m-%d')
        user_data['start_date'] = None
        user_data['current_usage_GB'] = 0
        endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
        return await self.make_patch_request(endpoint, user_data)

    async def update_package_days(self, uuid: str) -> bool:
        """Update the package days for a user."""
        user_data = await self.find_service(uuid)
        if not user_data:
            print("User not found.")
            return False
        user_data['last_reset_time'] = datetime.now().strftime('%Y-%m-%d')
        user_data['start_date'] = None
        endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
        return await self.make_patch_request(endpoint, user_data)

    async def update_traffic(self, uuid: str) -> bool:
        """Reset the traffic limit for a user to 0."""
        user_data = await self.find_service(uuid)
        if not user_data:
            print("User not found.")
            return False
        user_data['current_usage_GB'] = 0
        endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
        return await self.make_patch_request(endpoint, user_data)

    async def delete_user(self, uuid: str) -> bool:
        """Delete a user."""
        async with aiohttp.ClientSession() as session:
            try:
                endpoint = f"{self.base_url}/api/v2/admin/user/{uuid}/"
                async with session.delete(endpoint, headers=self.headers) as response:
                    return response.status == 200
            except aiohttp.ClientError as e:
                print(f"Error in delete_user: {e}")
                return False

    async def find_service(self, uuid: str) -> dict:
        """Find a service by UUID."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/v2/admin/user/{uuid}/", headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"User with UUID {uuid} not found.")
                        return {}
            except aiohttp.ClientError as e:
                print(f"Error in find_service: {e}")
                return {}

    async def backup_file(self) -> bytes:
        """Backup the file."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/admin/backup/backupfile/", headers=self.headers) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        print(f"Failed to retrieve backup file. Status code: {response.status}")
                        return None
            except aiohttp.ClientError as e:
                print(f"Error in backup_file: {e}")
                return None

    async def get_app_information(self, uuid: str) -> dict:
        """Get information about available apps for a given UUID."""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/{uuid}/api/v2/user/apps/"
                querystring = {"platform": "all"}
                headers = {"Accept": "application/json"}
                async with session.get(url, headers=headers, params=querystring) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print("Failed to fetch app information. Status code:", response.status)
                        return {}
            except aiohttp.ClientError as e:
                print(f"Error in get_app_information: {e}")
                return {}

    @staticmethod
    def generate_qr_code(data: str) -> BytesIO:
        """Generate a QR code for the given data."""
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        qr_img = qr.make_image
