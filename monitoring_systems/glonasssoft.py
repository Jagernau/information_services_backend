import json
import requests
import time

import sys
sys.path.append('../')
from information_services import config

# login = config.GLONASS_LOGIN # логин клиента
# password = config.GLONASS_PASS # логин клиента
# based_adres=str(config.GLONASS_BASED_ADRESS)

class Glonasssoft:
    """ 
    Получение данных с систем мониторинга Глонассофт
    """
    def __init__(self, login: str, password: str, based_adres: str):
        self.login = login
        self.password = password
        self.based_adres = based_adres

    def token(self):
        """Получение Токена Глонассофт"""
        time.sleep(1)
        url = f'{self.based_adres}v3/auth/login'
        data = {'login': self.login, 'password': self.password}
        headers = {'Content-type': 'application/json', 'accept': 'json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return response.json()["AuthId"]
        else:
            return None

    def _get_request(self, url, token):
        """Универсальный метод для выполнения GET-запросов"""
        headers = {
            "X-Auth": f"{token}",
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def _post_request(self, url, token, data: dict):
        """Универсальный метод для выполнения POST """
        headers = {
            "X-Auth": f"{token}",
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.text)

    def get_all_vehicles_old(self, token: str):
        """
        Метод получения всех объектов glonasssoft
        """
        time.sleep(1)
        return self._get_request(f"{self.based_adres}vehicles/", token)

    def get_expense(self, token, obj_id, start, end):
        """
        Метод получения расхода ТС
        """
        time.sleep(1)
        data = {
                "vehicleIds": [obj_id,],
                "from": str(start),
                "to": str(end),
            }
        return self._post_request(f"{self.based_adres}v3/vehicles/fuelConsumption", token, data)

    def get_refuel(self, token, obj_id, start, end):
        """
        Метод получения сливов заправок
        """
        time.sleep(1)
        data = {
                "vehicleIds": [obj_id,],
                "from": str(start),
                "to": str(end),
            }
        return self._post_request(f"{self.based_adres}v3/vehicles/fuelInOut", token, data)

# glonass = Glonasssoft(login, password, based_adres)
# glonass_token = glonass.token()
# print(glonass_token)
# # # # # all_vehicles = glonass.get_all_vehicles_old(str(glonass_token))
# expen_data = glonass.get_expense(glonass_token, 548938, "2024-11-18T00:01", "2024-11-18T23:59")
# print(expen_data[0])
# print(expen_data[0]["name"])
# print(expen_data[0]["periods"][0]["fuelLevelStart"])
# print(expen_data[0]["periods"][0]["fuelLevelEnd"])
# refuel_data = glonass.get_refuel(glonass_token, 548938, "2024-11-18T00:01", "2024-11-18T23:59")
# print(refuel_data[0])
# print(refuel_data[0])
# print(refuel_data[0])
# print(refuel_data[0])
# print(refuel_data[0])
