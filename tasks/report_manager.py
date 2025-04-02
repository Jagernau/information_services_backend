from datetime import timedelta

import sys

sys.path.append('../')
from information_services_backend.my_logger import logger
from information_services_backend.generating_reports.glonass_reports import GlonassReport
from information_services_backend.config import GLONASS_BASED_ADRESS

class ManageReport:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.report = None

    def __enter__(self):
        if self.kwargs["monitoring_sys"] == 1: #Глонасс
            rep = GlonassReport(
                self.kwargs["sys_login"],
                self.kwargs["sys_password"],
                GLONASS_BASED_ADRESS,
            )
            self.report = rep
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Clean up resources and handle exceptions."""
        if exc_type:
            logger.error(f"Exception in ManageReport")
        logger.info(f"Cleaning up resources for ManageReport")
        self.report = None

    def _get_interval_convert(self):
        now = self.kwargs["now_time"]
        if self.kwargs["service_counter"] == 0: # через 30мин
            return {
                    "end": now.strftime("%Y-%m-%dT%H:%M:%S"),
                    "start": (now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%S")
                    }
        if self.kwargs["service_counter"] == 1: # за предыдущий день
            yesterday = now - timedelta(days=1)
            return {
                    "start": yesterday.strftime("%Y-%m-%dT00:01"),
                    "end": yesterday.strftime("%Y-%m-%dT23:59") 
                    }
        if self.kwargs["service_counter"] == 2: # за предыдущюю неделю
            yesterday = now - timedelta(days=1)
            last_week = yesterday - timedelta(weeks=1)
            return {
                "start": last_week.strftime("%Y-%m-%dT00:01"),
                "end": yesterday.strftime("%Y-%m-%dT23:59")
            }
        if self.kwargs["service_counter"] == 3: # за предыдущий месяц
            last_month = now.replace(day=1) - timedelta(days=1)
            return {
                "start": last_month.replace(day=1).strftime("%Y-%m-%dT00:01"),
                "end": last_month.strftime("%Y-%m-%dT23:59")
            }

    def get_sys_mon_report(self):
        "Выполняет и возвращает отчёт"
        if self.kwargs["monitoring_sys"] == 1: #Глонасс
            if self.report is None:
                raise ValueError("Report resource not initialized.")

            if self.kwargs['info_obj_serv_id'] == 5: #СливЗаправ
                interval = self._get_interval_convert()
                result = self.report.get_fuel_up_down(
                        self.kwargs["sys_id_obj"],
                        interval["start"],
                        interval["end"]
                        )
                return result

            if self.kwargs['info_obj_serv_id'] == 6: #Расход
                interval = self._get_interval_convert()
                result = self.report.get_fuel_flow(
                        self.kwargs["sys_id_obj"],
                        interval["start"],
                        interval["end"]
                        )
                return result

            if self.kwargs['info_obj_serv_id'] == 7: #Сливы
                interval = self._get_interval_convert()
                result = self.report.get_fuel_down(  #Сливы
                        self.kwargs["sys_id_obj"],
                        interval["start"],
                        interval["end"]
                        )
                return result

            if self.kwargs['info_obj_serv_id'] == 8: #Заправки
                interval = self._get_interval_convert()
                result = self.report.get_fuel_up(  #Заправки
                        self.kwargs["sys_id_obj"],
                        interval["start"],
                        interval["end"]
                        )
                return result

        if self.kwargs["monitoring_sys"] == 2:
            pass
        if self.kwargs["monitoring_sys"] == 3:
            pass
        if self.kwargs["monitoring_sys"] == 4:
            pass


        

