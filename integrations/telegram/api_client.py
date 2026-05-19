import os
import logging
import aiohttp
from typing import Dict, Any, List, Optional
from decouple import config

logger = logging.getLogger(__name__)

# Load configurations
API_BASE_URL = config("API_BASE_URL", default="http://web:8000/api/")
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN", default="")

class CRMAPIClient:
    """
    Asynchronous client for interacting with the Django REST API.
    Used by the standalone Aiogram bot.
    """
    def __init__(self):
        self.base_url = API_BASE_URL.rstrip("/")
        self.headers = {
            "X-Bot-Token": TELEGRAM_BOT_TOKEN,
            "Content-Type": "application/json"
        }

    async def _request(
        self, method: str, path: str, json_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        logger.info(f"🤖 Bot API Request: {method} {url}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json_data,
                    timeout=10
                ) as response:
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        text = await response.text()
                        logger.error(f"❌ API Error [{response.status}]: {text}")
                        return None
            except Exception as e:
                logger.error(f"❌ Connection error to backend: {str(e)}")
                return None

    async def get_or_create_customer(self, phone: str, first_name: str, telegram_id: str) -> Optional[Dict[str, Any]]:
        """
        Links or registers a customer phone with a Telegram ID.
        """
        payload = {
            "phone": phone,
            "first_name": first_name,
            "telegram_id": str(telegram_id)
        }
        return await self._request("POST", "customers/by-phone/", payload)

    async def get_upcoming_bookings(self, telegram_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all upcoming active bookings for a customer by Telegram ID.
        """
        res = await self._request("GET", f"appointments/by-telegram/{telegram_id}/")
        return res if res is not None else []

    async def get_barbershops(self) -> List[Dict[str, Any]]:
        """
        Retrieves list of all barbershops (branches).
        """
        res = await self._request("GET", "barbershops/")
        if isinstance(res, dict) and "results" in res:
            return res["results"]
        return res if isinstance(res, list) else []

    async def get_services(self) -> List[Dict[str, Any]]:
        """
        Retrieves list of active services.
        """
        res = await self._request("GET", "services/")
        if isinstance(res, dict) and "results" in res:
            return res["results"]
        return res if isinstance(res, list) else []

    async def get_staff(self) -> List[Dict[str, Any]]:
        """
        Retrieves list of active barbers (staff).
        """
        res = await self._request("GET", "staff/")
        if isinstance(res, dict) and "results" in res:
            return res["results"]
        return res if isinstance(res, list) else []

    async def create_booking(
        self, customer_id: int, staff_id: int, service_id: int, start_time: str, barbershop_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a new appointment.
        """
        payload = {
            "customer": customer_id,
            "staff": staff_id,
            "service": service_id,
            "start_time": start_time
        }
        if barbershop_id:
            payload["barbershop"] = barbershop_id
        return await self._request("POST", "appointments/", payload)

    async def transition_booking(self, booking_id: int, new_status: str) -> Optional[Dict[str, Any]]:
        """
        Transitions appointment status (e.g. cancels or confirms booking).
        """
        payload = {"new_status": new_status}
        return await self._request("POST", f"appointments/{booking_id}/transition/", payload)

    async def get_clients(self) -> List[Dict[str, Any]]:
        """
        Retrieves list of all clients (customers).
        """
        res = await self._request("GET", "clients/")
        if isinstance(res, dict) and "results" in res:
            return res["results"]
        return res if isinstance(res, list) else []

    async def get_global_stats(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves global SaaS dashboard statistics (Total branches, barbers, revenue, etc.).
        """
        return await self._request("GET", "admin/global-stats/")


