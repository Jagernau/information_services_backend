# monitoring_systems/glonasssoft.py
import aiohttp
import asyncio
from typing import Optional
import random
import sys
sys.path.append('../')
from information_services_backend.my_logger import logger

class Glonasssoft:
    """
    Асинхронный клиент для получения данных с систем мониторинга Глонассофт.
    """
    def __init__(self, login: str, password: str, based_adres: str):
        self.login = login
        self.password = password
        self.based_adres = based_adres

    async def gen_random_num(self):
        return random.uniform(1.2, 3.7)

    async def token(self) -> Optional[str]:
        await asyncio.sleep(await self.gen_random_num())
        """Получение токена авторизации."""
        url = f'{self.based_adres}v3/auth/login'
        data = {'login': self.login, 'password': self.password}
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    json_response = await response.json()
                    return json_response.get("AuthId")
                else:
                    await asyncio.sleep(await self.gen_random_num())
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=data, headers=headers) as response:
                            if response.status == 200:
                                json_response = await response.json()
                                return json_response.get("AuthId")
                            else:
                                logger.error(f"TOKEN request failed: {response.text}")
                                return None

    async def _get_request(self, url: str, token: str) -> Optional[dict]:
        """Асинхронный метод для выполнения GET-запросов."""
        headers = {
            "X-Auth": f"{token}",
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        await asyncio.sleep(await self.gen_random_num())
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    await asyncio.sleep(await self.gen_random_num())
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                return await response.json()
                            else:
                            
                                logger.error(f"GET request failed: {response.text}")
                                return None


    async def _post_request(self, url: str, token: str, data: dict) -> Optional[dict]:
        """Асинхронный метод для выполнения POST-запросов."""
        headers = {
            "X-Auth": f"{token}",
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        await asyncio.sleep(await self.gen_random_num())
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    await asyncio.sleep(await self.gen_random_num())
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, headers=headers, json=data) as response:
                            if response.status == 200:
                                return await response.json()
                            else:
                                logger.error(f"POST request failed: {response.text}")
                                return None
                                

    async def get_all_vehicles_old(self, token: str) -> Optional[dict]:
        """Метод получения всех объектов Glonasssoft."""
        await asyncio.sleep(await self.gen_random_num())
        url = f"{self.based_adres}vehicles/"
        return await self._get_request(url, token)

    async def get_expense(self, token: str, obj_id: int, start: str, end: str) -> Optional[dict]:
        """Метод получения расхода топлива ТС."""
        await asyncio.sleep(await self.gen_random_num())
        url = f"{self.based_adres}v3/vehicles/fuelConsumption"
        data = {
            "vehicleIds": [obj_id],
            "from": start,
            "to": end
        }
        return await self._post_request(url, token, data)

    async def get_refuel(self, token: str, obj_id: int, start: str, end: str) -> Optional[dict]:
        """Метод получения данных о сливе и заправке топлива."""
        await asyncio.sleep(await self.gen_random_num())
        url = f"{self.based_adres}v3/vehicles/fuelInOut"
        data = {
            "vehicleIds": [obj_id],
            "from": start,
            "to": end
        }
        return await self._post_request(url, token, data)

