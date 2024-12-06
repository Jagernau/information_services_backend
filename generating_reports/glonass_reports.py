# generating_reports/glonass_reports.py
import asyncio
from datetime import datetime, timedelta
from monitoring_systems.glonasssoft import Glonasssoft
import sys
sys.path.append('../')
from information_services_backend.my_logger import logger

class GlonassReport:
    """
    Асинхронные отчёты Glonasssoft.
    """
    def __init__(self, login: str, password: str, based_adress: str):
        self.glonass_client = Glonasssoft(login, password, based_adress)

    async def get_yest_serv_fuel_flow(self, obj_id: int):
        """
        Отчёт по расходу топлива за предыдущий день.
        """
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        yest_start = yesterday.strftime("%Y-%m-%dT00:01")
        yest_end = yesterday.strftime("%Y-%m-%dT23:59")

        try:
            await asyncio.sleep(1)
            token = await self.glonass_client.token()
            if not token:
                return "Не удалось получить токен."

            await asyncio.sleep(1)
            data = await self.glonass_client.get_expense(token, obj_id, yest_start, yest_end)
            if not data:
                return None

            name = data[0]["name"]
            start_val = data[0]["periods"][0]["fuelLevelStart"]
            end_val = data[0]["periods"][0]["fuelLevelEnd"]
            all_exp = data[0]["periods"][0]["fuelConsumption"]
            move_exp = data[0]["periods"][0]["fuelConsumptionMove"]

            return (
                f"Отчёт по расходу топлива\nТС - {name}\n"
                f"Период: {yest_start} - {yest_end}\n"
                f"Начальный уровень: {start_val}\nКонечный уровень: {end_val}\n"
                f"Полный расход: {all_exp}\nРасход в движении: {move_exp}"
            )
        except Exception as e:
            logger.error(f"ошибка получения данных {e}")
            return None

    async def get_yest_serv_fuel_up_down(self, obj_id: int):
        """
        Отчёт по сливам и заправкам за предыдущий день.
        """
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        yest_start = yesterday.strftime("%Y-%m-%dT00:01")
        yest_end = yesterday.strftime("%Y-%m-%dT23:59")

        try:
            await asyncio.sleep(1)
            token = await self.glonass_client.token()
            if not token:
                return "Не удалось получить токен."

            await asyncio.sleep(1)
            data = await self.glonass_client.get_refuel(token, obj_id, yest_start, yest_end)
            if not data:
                return "Не удалось получить данные о заправках и сливах."

            name = data[0]["name"]
            fuels = data[0].get("fuels", [])
            if not fuels:
                return None
                #return f"По ТС {name} заправок и сливов не было за период {yest_start} - {yest_end}."

            result = f"Отчёт по заправкам и сливам ТС - {name}\n"
            for fuel in fuels:
                event = "ЗАПРАВКА" if fuel["event"] == "FuelIn" else "СЛИВ"
                result += (
                    f"{event}:\n"
                    f"Начало: {fuel['startDate']}\n"
                    f"Окончание: {fuel['endDate']}\n"
                    f"Количество: {round(fuel['valueFuel'], 1)}\n"
                    f"Топливо до: {round(fuel['fuelStart'], 1)}\n"
                    f"Топливо после: {round(fuel['fuelEnd'], 1)}\n"
                    "*****\n"
                )
            return result
        except Exception as e:
            logger.error(f"ошибка получения данных {e}")
            return None

    async def get_now_serv_fuel_up_down(self, obj_id):
        """
        Отчёт по сливам и заправкам по топливу за интервал
        """
        today_now = datetime.now()

        # Вычисляем вчерашний день
        tuday_count = today_now - timedelta(minutes=5)

        # Форматируем начало и конец дня в нужный формат
        start = today_now.strftime("%Y-%m-%dT%H:%M:%S")
        end = tuday_count.strftime("%Y-%m-%dT%H:%M:%S")
        try:
            await asyncio.sleep(1)
            glonass_token = await self.glonass_client.token()
            await asyncio.sleep(1)
            expen_data = await self.glonass_client.get_refuel(
                    glonass_token,
                    obj_id,
                    start,
                    end
                    )
        except Exception as e:
            logger.error(f"ошибка получения данных {e}")
            return None
        else:
            name = expen_data[0]["name"]
            fuels = expen_data[0]["fuels"] if len(expen_data[0]["fuels"]) >= 1 else None
            result = f"Отчёт по заправкам и сливам ТС - {name}\n"
            if fuels == None:
                return None
            else:
                fuelsUp_list = [i for i in fuels if i["event"] == "FuelIn"]
                fuelsUps = fuelsUp_list if len(fuelsUp_list) >= 1 else None

                fuelsOut_list = [i for i in fuels if i["event"] == "FuelOut"]
                fuelsOuts = fuelsOut_list if len(fuelsOut_list) >= 1 else None

                if fuelsUps == None and fuelsOuts == None:
                    return None

                if fuelsUps != None and fuelsOuts == None:
                    for i in fuelsUps:
                        result += f"ЗАПРАВКИ:\nВремя начала - {i['startDate']}\nВремя окончания - {i['endDate']}\nЗаправленно - {round(i['valueFuel'], 1)}\nТопливо до заправки - {round(i['fuelStart'], 1)}\nТопливо после заправки - {round(i['fuelEnd'], 1)}\n*****\n"
                    return result

                if fuelsUps == None and fuelsOuts != None:
                    for i in fuelsOuts:
                        result += f"СЛИВЫ:\nВремя начала - {i['startDate']}\nВремя окончания - {i['endDate']}\nСлито - {round(i['valueFuel'], 1)}\nТопливо до слива - {round(i['fuelStart'], 1)}\nТопливо после слива - {round(i['fuelEnd'], 1)}\n*****\n"
                    return result

                if fuelsUps != None and fuelsOuts != None:
                    for i in fuelsUps:
                        result += f"ЗАПРАВКИ:\nВремя начала - {i['startDate']}\nВремя окончания - {i['endDate']}\nЗаправленно - {round(i['valueFuel'], 1)}\nТопливо до заправки - {round(i['fuelStart'], 1)}\nТопливо после заправки - {round(i['fuelEnd'], 1)}\n*****\n"

                    for i in fuelsOuts:
                        result += f"СЛИВЫ:\nВремя начала - {i['startDate']}\nВремя окончания - {i['endDate']}\nСлито - {round(i['valueFuel'], 1)}\nТопливо до слива - {round(i['fuelStart'], 1)}\nТопливо после слива - {round(i['fuelEnd'], 1)}\n*****\n"
                    return result
