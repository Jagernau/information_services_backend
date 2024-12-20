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

    def get_fuel_flow(self, obj_id, start, end):
        """
        Отчёт по расходу топлива за предыдущий день
        """
        try:
            glonass_token = self.glonass_class.token()
            expen_data = self.glonass_class.get_expense(
                    glonass_token,
                    int(obj_id),
                    start,
                    end
                    )
            name = expen_data[0]["name"]
            start_val = expen_data[0]["periods"][0]["fuelLevelStart"]
            end_val = expen_data[0]["periods"][0]["fuelLevelEnd"]
            all_exp = expen_data[0]["periods"][0]["fuelConsumption"]
            move_exp = expen_data[0]["periods"][0]["fuelConsumptionMove"]
            result = f"Отчёт по расходу\nТС - {name}\nОтчёт {start} - {end}\nНачальный уровень - {start_val}\nКонечный уровень - {end_val}\nПолный расход - {all_exp}\nРасход в движении - {move_exp}"
            return result
        except Exception as e:
            logger.error(f"Не получен отчёт расход по топливу {e}")
            return None


    def get_fuel_up_down(self, obj_id, start, end):
        """
        Отчёт по сливам и заправкам по топливу за интервал
        """
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


    def get_fuel_down(self, obj_id, start, end):
        """
        Отчёт по сливам за интервал
        """
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
            result = f"Отчёт по сливам ТС - {name}\n"
            if fuels == None:
                logger.error(f"Нет движения топлива get_yest_serv_fuel_up_down")
                return None
            else:
                fuelsOut_list = [i for i in fuels if i["event"] == "FuelOut"]
                fuelsOuts = fuelsOut_list if len(fuelsOut_list) >= 1 else None

                if fuelsOuts == None:
                    return None

                if fuelsOuts != None:
                    for i in fuelsOuts:
                        result += f"СЛИВЫ:\nВремя начала - {i['startDate']}\nВремя окончания - {i['endDate']}\nСлито - {round(i['valueFuel'], 1)}\nТопливо до слива - {round(i['fuelStart'], 1)}\nТопливо после слива - {round(i['fuelEnd'], 1)}\n*****\n"
                    return result


    def get_fuel_up(self, obj_id, start, end):
        """
        Отчёт по заправкам по топливу за интервал
        """
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

                if fuelsUps == None:
                    return None

                if fuelsUps != None:
                    for i in fuelsUps:
                        result += f"ЗАПРАВКИ:\nВремя начала - {i['startDate']}\nВремя окончания - {i['endDate']}\nЗаправленно - {round(i['valueFuel'], 1)}\nТопливо до заправки - {round(i['fuelStart'], 1)}\nТопливо после заправки - {round(i['fuelEnd'], 1)}\n*****\n"
                    return result

