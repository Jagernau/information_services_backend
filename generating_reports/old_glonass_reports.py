from datetime import datetime, timedelta, date

import sys
sys.path.append('../')
from information_services_backend.my_logger import logger

class GlonassReport:
    """
    Отчёты глонасс
    """
    def __init__(self, login, password, based_adress):
        from monitoring_systems import glonasssoft

        self.login = login
        self.password = password
        self.based_adres = based_adress
        self.glonass_class = glonasssoft.Glonasssoft(
                login,
                password,
                based_adress)

    def get_yest_serv_fuel_flow(self, obj_id):
        """
        Отчёт по расходу топлива за предыдущий день
        """
        today = datetime.now()

        # Вычисляем вчерашний день
        yesterday = today - timedelta(days=1)

        # Форматируем начало и конец дня в нужный формат
        yest_start = yesterday.strftime("%Y-%m-%dT00:01")
        yest_end = yesterday.strftime("%Y-%m-%dT23:59")
        try:
            glonass_token = self.glonass_class.token()
            expen_data = self.glonass_class.get_expense(
                    glonass_token,
                    int(obj_id),
                    yest_start,
                    yest_end
                    )
            name = expen_data[0]["name"]
            start_val = expen_data[0]["periods"][0]["fuelLevelStart"]
            end_val = expen_data[0]["periods"][0]["fuelLevelEnd"]
            all_exp = expen_data[0]["periods"][0]["fuelConsumption"]
            move_exp = expen_data[0]["periods"][0]["fuelConsumptionMove"]
            result = f"Отчёт по расходу\nТС - {name}\nОтчёт {yest_start} - {yest_end}\nНачальный уровень - {start_val}\nКонечный уровень - {end_val}\nПолный расход - {all_exp}\nРасход в движении - {move_exp}"
            return result
        except:
            logger.error(f"Не получен отчёт расход по топливу")
            return None

    def get_yest_serv_fuel_up_down(self, obj_id):
        """
        Отчёт по сливам и заправкам по топливу за предыдущий день
        """
        today = datetime.now()

        # Вычисляем вчерашний день
        yesterday = today - timedelta(days=1)

        # Форматируем начало и конец дня в нужный формат
        yest_start = yesterday.strftime("%Y-%m-%dT00:01")
        yest_end = yesterday.strftime("%Y-%m-%dT23:59")
        try:
            glonass_token = self.glonass_class.token()
            expen_data = self.glonass_class.get_refuel(
                    glonass_token,
                    obj_id,
                    yest_start,
                    yest_end
                    )
        except Exception as e:
            logger.error(f"Не получен отчёт по сливам и заправкам get_yest_serv_fuel_up_down {e}")
            return None
        else:
            if len(expen_data) == 0:
                return None
            name = expen_data[0]["name"]
            fuels = expen_data[0]["fuels"] if len(expen_data[0]["fuels"]) >= 1 else None
            result = f"Отчёт по заправкам и сливам ТС - {name}\n"
            if fuels == None:
                logger.error(f"Нет двидения топлива get_yest_serv_fuel_up_down")
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

    def get_now_serv_fuel_up_down(self, obj_id):
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
            glonass_token = self.glonass_class.token()
            expen_data = self.glonass_class.get_refuel(
                    glonass_token,
                    obj_id,
                    start,
                    end
                    )
        except Exception as e:
            logger.error(f"Не удаётсся получить отчёт в get_now_serv_fuel_up_down {e}")
            return None
        else:
            if len(expen_data) == 0:
                return None
            name = expen_data[0]["name"]
            fuels = expen_data[0]["fuels"] if len(expen_data[0]["fuels"]) >= 1 else None
            result = f"Отчёт по заправкам и сливам ТС - {name}\n"
            if fuels == None:
                logger.error(f"Нет движения топлива get_yest_serv_fuel_up_down")
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
