from datetime import datetime, timedelta
import time
import sys
sys.path.append('../')
from information_services_backend.my_logger import logger
from information_services_backend.generating_reports.glonass_reports import GlonassReport
from information_services_backend.config import GLONASS_BASED_ADRESS


class TaskGenerator:
    """
    Генератор задач с проверкой времени выполнения.
    """

    def __init__(self):
        self.all_tasks = []

    def _get_now_time(self):
        """Возвращает текущее время."""
        return datetime.now()

    def _should_run_report(self, service_counter, now_time):
        """Проверяет, нужно ли выполнять отчёт в текущее время."""
        if service_counter == 0:
            return True  # Мгновенный отчёт выполняется каждые 5 минут
        elif service_counter == 1:
            return now_time.hour == 9 and now_time.minute in range(6)
        elif service_counter == 2:
            return now_time.weekday() == 0 and now_time.hour == 0 and now_time.minute == 0
        elif service_counter == 3:
            return now_time.day == 1 and now_time.hour == 0 and now_time.minute == 0
        return False

    def _execute_report(self, serv_obj_id, sys_login, sys_password, info_obj_serv_id, sys_id_obj):
        """Выполняет отчёт и обрабатывает ошибки."""
        logger.info(f"Выполняется отчёт для задачи {serv_obj_id}")
        try:
            if info_obj_serv_id == 2:
                glonas_report = GlonassReport(str(sys_login), str(sys_password), GLONASS_BASED_ADRESS)
                result = glonas_report.get_now_serv_fuel_up_down(sys_id_obj)
                logger.info(f"Отчёт по {serv_obj_id}: {result}")
        except Exception as e:
            logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {serv_obj_id}: {e}")

    def make_report(self,
                    serv_obj_id,
                    serv_obj_sys_mon_id,
                    info_obj_serv_id,
                    subscription_start,
                    subscription_end,
                    tel_num_user,
                    service_counter,
                    stealth_type,
                    monitoring_sys,
                    sys_id_obj,
                    sys_login,
                    sys_password):
        """Определяет, какой отчёт выполнять и когда."""
        now_time = self._get_now_time()
        
        if subscription_start < now_time < subscription_end and self._should_run_report(service_counter, now_time):
            self._execute_report(serv_obj_id, sys_login, sys_password, info_obj_serv_id, sys_id_obj)

            # Ждем перед следующим выполнением в зависимости от типа отчёта
            if service_counter in [0]:  # мгновенно
                time.sleep(300)  # ждем 5 минут
            else: 
                time.sleep(60)  # ждем минуту для других типов

    def get_unic_all_tasks(self):
        return {task["serv_obj_id"] for task in self.all_tasks}

    def starter_task(self,
                     serv_obj_id,
                     serv_obj_sys_mon_id,
                     info_obj_serv_id,
                     subscription_start,
                     subscription_end,
                     tel_num_user,
                     service_counter,
                     stealth_type,
                     monitoring_sys,
                     sys_id_obj,
                     sys_login,
                     sys_password):
        """Запускает задачу и удаляет её после завершения."""
        
        self.all_tasks.append({
            'serv_obj_id': serv_obj_id,
            'serv_obj_sys_mon_id': serv_obj_sys_mon_id,
            'info_obj_serv_id': info_obj_serv_id,
            'subscription_start': subscription_start,
            'subscription_end': subscription_end,
            'tel_num_user': tel_num_user,
            'service_counter': service_counter,
            'stealth_type': stealth_type,
            'monitoring_sys': monitoring_sys,
            'sys_id_obj': sys_id_obj,
            'sys_login': sys_login,
            'sys_password': sys_password,
        })

        while True:
            now_time = self._get_now_time()
            if subscription_start < now_time < subscription_end:
                logger.info(f"Задача {serv_obj_id} работает, текущее время: {now_time}")
                self.make_report(serv_obj_id, serv_obj_sys_mon_id, info_obj_serv_id, subscription_start, subscription_end, tel_num_user, service_counter, stealth_type, monitoring_sys, sys_id_obj, sys_login, sys_password)

            else:
                logger.info(f"Задача {serv_obj_id} завершена или вышла за границы времени.")
                self.all_tasks = [task for task in self.all_tasks if task["serv_obj_id"] != serv_obj_id]
                logger.info(f'Задача {serv_obj_id} завершена и удалена из коллектора задач.')
                break

            time.sleep(1)

