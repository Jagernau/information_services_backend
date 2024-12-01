from datetime import datetime, timedelta


class GlonassReport:
    """
    Отчёты ГЛОНАСС
    """
    def __init__(self, login, password, based_adress):
        from monitoring_systems import glonasssoft

        self.login = login
        self.password = password
        self.based_adres = based_adress
        self.glonass_class = glonasssoft.Glonasssoft(login, password, based_adress)

    def _format_datetime(self, dt, fmt="%Y-%m-%dT%H:%M:%S"):
        return dt.strftime(fmt)

    def _get_time_range(self, days_offset=0, minutes_offset=0):
        now = datetime.now()
        start = now - timedelta(days=days_offset, minutes=minutes_offset)
        return self._format_datetime(start), self._format_datetime(now)

    def _generate_fuel_report(self, fuels, name, start, end):
        if not fuels:
            return f"По ТС {name} сливы и заправки отсутствуют за период {start} - {end}"

        result = f"Отчёт по заправкам и сливам ТС - {name}\n"
        events = {
            "FuelIn": "ЗАПРАВКИ",
            "FuelOut": "СЛИВЫ"
        }

        for event, title in events.items():
            event_list = [f for f in fuels if f["event"] == event]
            if event_list:
                result += f"{title}:\n"
                for i in event_list:
                    result += (
                        f"Время начала - {i['startDate']}\n"
                        f"Время окончания - {i['endDate']}\n"
                        f"{'Заправлено' if event == 'FuelIn' else 'Слито'} - {round(i['valueFuel'], 1)}\n"
                        f"Топливо до - {round(i['fuelStart'], 1)}\n"
                        f"Топливо после - {round(i['fuelEnd'], 1)}\n*****\n"
                    )
        return result

    def _fetch_data(self, obj_id, start, end, method_name):
        try:
            glonass_token = self.glonass_class.token()
            method = getattr(self.glonass_class, method_name)
            return method(glonass_token, obj_id, start, end)
        except:
            return None

    def get_yest_serv_fuel_flow(self, obj_id):
        """
        Отчёт по расходу топлива за предыдущий день
        """
        yest_start, yest_end = self._get_time_range(days_offset=1)
        expen_data = self._fetch_data(obj_id, yest_start, yest_end, "get_expense")

        if not expen_data:
            return None

        data = expen_data[0]
        name = data["name"]
        periods = data["periods"][0]
        return (
            f"Отчёт по расходу\n"
            f"ТС - {name}\n"
            f"Отчёт {yest_start} - {yest_end}\n"
            f"Начальный уровень - {periods['fuelLevelStart']}\n"
            f"Конечный уровень - {periods['fuelLevelEnd']}\n"
            f"Полный расход - {periods['fuelConsumption']}\n"
            f"Расход в движении - {periods['fuelConsumptionMove']}"
        )

    def get_yest_serv_fuel_up_down(self, obj_id):
        """
        Отчёт по сливам и заправкам топлива за предыдущий день
        """
        yest_start, yest_end = self._get_time_range(days_offset=1)
        expen_data = self._fetch_data(obj_id, yest_start, yest_end, "get_refuel")

        if not expen_data:
            return None

        name = expen_data[0]["name"]
        fuels = expen_data[0].get("fuels", [])
        return self._generate_fuel_report(fuels, name, yest_start, yest_end)

    def get_now_serv_fuel_up_down(self, obj_id):
        """
        Отчёт по сливам и заправкам топлива за последние 5 минут
        """
        start, end = self._get_time_range(minutes_offset=5)
        expen_data = self._fetch_data(obj_id, start, end, "get_refuel")

        if not expen_data:
            return None

        name = expen_data[0]["name"]
        fuels = expen_data[0].get("fuels", [])
        return self._generate_fuel_report(fuels, name, start, end)
