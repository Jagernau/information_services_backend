import sys
import os
from jinja2 import Environment, FileSystemLoader

sys.path.append('../')
from information_services_backend.my_logger import logger

class GlonassReport:
    """
    Отчёты глонасс с генерацией HTML через Jinja
    """
    def __init__(self, login, password, based_adress):
        from monitoring_systems import glonasssoft
        
        # Инициализация Jinja
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_path))
        self.env.filters['round'] = lambda x, precision: round(x, precision)

        self.login = login
        self.password = password
        self.based_adres = based_adress
        self.glonass_class = glonasssoft.Glonasssoft(
            login,
            password,
            based_adress
        )

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
            context = {
                'name': name,
                'start': start,
                'end': end,
                'start_val': start_val,
                'end_val': end_val,
                'all_exp': all_exp,
                'move_exp': move_exp
            }
            template = self.env.get_template('fuel_flow.html')

            if end_val and all_exp and move_exp:
                try:
                    return template.render(context)
                except Exception as e:
                    logger.error(f"Ошибка в шаблоне get_fuel_flow {e}")
                    return None


            else:
                return None
        except Exception as e:
            logger.error(f"Не получен отчёт get_fuel_flow {e}")
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
                    context = {
                        'name': expen_data[0]["name"],
                        'fuelsUps': fuelsUps,
                        'fuelsOuts': None
                    }
                    try:
                        template = self.env.get_template('fuel_up_down.html')
                        return template.render(context)
                    except Exception as e:
                        logger.error(f"Ошибка при создании шаблона get_fuel_up_down {e}")
                        return None


                if fuelsUps == None and fuelsOuts != None:
                    context = {
                        'name': expen_data[0]["name"],
                        'fuelsUps': None,
                        'fuelsOuts': fuelsOuts
                    }
                    try:
                        template = self.env.get_template('fuel_up_down.html')
                        return template.render(context)
                    except Exception as e:
                        logger.error(f"Ошибка при создании шаблона get_fuel_up_down {e}")
                        return None


                if fuelsUps != None and fuelsOuts != None:
                    context = {
                        'name': expen_data[0]["name"],
                        'fuelsUps': fuelsUps,
                        'fuelsOuts': fuelsOuts
                    }
                    try:
                        template = self.env.get_template('fuel_up_down.html')
                        return template.render(context)
                    except Exception as e:
                        logger.error(f"Ошибка при создании шаблона get_fuel_up_down {e}")
                        return None


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
            logger.error(f"Не удаётсся получить отчёт в get_now_serv_down {e}")
            return None
        else:
            if len(expen_data) == 0:
                return None
            fuels = expen_data[0]["fuels"] if len(expen_data[0]["fuels"]) >= 1 else None
            if fuels == None:
                logger.error(f"Нет движения топлива get_yest_serv_fuel_up_down")
                return None
            else:
                fuelsOut_list = [i for i in fuels if i["event"] == "FuelOut"]
                fuelsOuts = fuelsOut_list if len(fuelsOut_list) >= 1 else None

                if fuelsOuts == None:
                    return None

                if fuelsOuts != None:
                    context = {
                        'name': expen_data[0]["name"],
                        'fuelsOuts': fuelsOuts
                    }
                    try:
                        template = self.env.get_template('fuel_down.html')
                        return template.render(context)
                    except Exception as e:
                        logger.error(f"Ошибка при создании шаблона get_now_serv_fuel_down {e}")
                        return None



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
            fuels = expen_data[0]["fuels"] if len(expen_data[0]["fuels"]) >= 1 else None
            if fuels == None:
                logger.error(f"Нет движения топлива get_yest_serv_fuel_up")
                return None
            else:
                fuelsUp_list = [i for i in fuels if i["event"] == "FuelIn"]
                fuelsUps = fuelsUp_list if len(fuelsUp_list) >= 1 else None

                if fuelsUps == None:
                    return None

                if fuelsUps != None:
                    context = {
                        'name': expen_data[0]["name"],
                        'fuelsUps': fuelsUps
                    }
                    try:
                        template = self.env.get_template('fuel_up.html')
                        return template.render(context)
                    except Exception as e:
                        logger.error(f"Ошибка при создании шаблона get_fuel_up {e}")
                        return None
