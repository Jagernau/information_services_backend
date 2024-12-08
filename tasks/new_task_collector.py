from datetime import datetime, timedelta
import time
from threading import Thread, Event
from typing import Dict, Any, Optional, Set
import random
from information_services_backend.my_logger import logger
from information_services_backend.generating_reports.glonass_reports import GlonassReport
from information_services_backend.config import GLONASS_BASED_ADRESS

class TaskGenerator:
    """
    Генератор задач с проверкой времени выполнения.
    """

    def __init__(self):
        self.all_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_registry: Dict[str, Dict[str, Any]] = {}

    def _get_now_time(self) -> datetime:
        """Возвращает текущее время."""
        return datetime.now()

    def get_unic_all_tasks(self) -> Set[str]:
        """Возвращает множество уникальных идентификаторов задач."""
        return set(self.task_registry.keys())

    def gen_random_num(self) -> float:
        """Генерирует случайное число."""
        return random.uniform(1.2, 3.7)

    def stop_task(self, serv_obj_id: str) -> None:
        """Останавливает задачу по идентификатору."""
        if serv_obj_id in self.task_registry:
            logger.info(f"Остановка задачи {serv_obj_id}")
            self.task_registry[serv_obj_id]['stop_event'].set()
            self.task_registry[serv_obj_id]['thread'].join()
            del self.task_registry[serv_obj_id]
            logger.info(f"Задача {serv_obj_id} остановлена.")

    def _generate_glonass_report(self, report_type: str, **kwargs) -> Optional[str]:
        """Генерация отчёта Glonass."""
        try:
            glonass_report = GlonassReport(
                str(kwargs['sys_login']),
                str(kwargs['sys_password']),
                GLONASS_BASED_ADRESS
            )
            obj_id = kwargs['sys_id_obj']
            if report_type == "now":
                return glonass_report.get_now_serv_fuel_up_down(obj_id)
            elif report_type == "yesterday_flow":
                return glonass_report.get_yest_serv_fuel_flow(obj_id)
            elif report_type == "yesterday_up_down":
                return glonass_report.get_yest_serv_fuel_up_down(obj_id)
        except Exception as e:
            logger.error(f"Ошибка генерации отчёта: {e}")
        return None

    def _save_report_to_db(self, result: str, now_time: datetime, **kwargs) -> None:
        """Сохраняет отчёт в базу данных."""
        try:
            from information_services_backend.data_base import crud
            monitoring_sys_name = crud.get_sys_mon_name(kwargs['monitoring_sys'])
            obj_name = crud.get_obj_name(kwargs['serv_obj_sys_mon_id'])
            cl_data = crud.get_client_name(kwargs['sys_login'], kwargs['sys_password'])
            crud.add_report_to_three(
                time_event=now_time,
                id_serv_subscription=kwargs['serv_obj_id'],
                processing_status=0,
                monitoring_system=monitoring_sys_name,
                object_name=obj_name,
                client_name=cl_data[0],
                it_name=cl_data[1],
                necessary_treatment=kwargs['stealth_type'],
                result=result,
                login=kwargs['sys_login']
            )
            logger.info(f"Отчёт отправлен в базу данных: {kwargs['serv_obj_id']} {result}")
        except Exception as e:
            logger.error(f"Ошибка сохранения отчёта в базу данных: {kwargs['serv_obj_id']} {e}")

    def make_report(self, now_time: datetime, **kwargs) -> None:
        """Создаёт отчёт на основе заданного интервала."""
        serv_obj_id = kwargs['serv_obj_id']
        service_counter = kwargs['service_counter']
        result = None

        try:
            if service_counter == 0:
                logger.info(f"Мгновенный отчёт для задачи {serv_obj_id}")
                result = self._generate_glonass_report("now", **kwargs)
                time.sleep(300)  # Задержка 5 минут
            elif service_counter == 1 and now_time.hour == 9 and now_time.minute < 6:
                logger.info(f"Ежедневный отчёт для задачи {serv_obj_id}")
                result = self._generate_glonass_report("yesterday_up_down", **kwargs)
                time.sleep(60)
            elif service_counter == 2 and now_time.weekday() == 0 and now_time.hour == 0 and now_time.minute == 0:
                logger.info(f"Еженедельный отчёт для задачи {serv_obj_id}")
                result = self._generate_glonass_report("yesterday_flow", **kwargs)
                time.sleep(60 * 60 * 24)
            elif service_counter == 3 and now_time.day == 1 and now_time.hour == 0 and now_time.minute == 0:
                logger.info(f"Ежемесячный отчёт для задачи {serv_obj_id}")
                result = self._generate_glonass_report("yesterday_flow", **kwargs)
                time.sleep(60 * 60 * 24)

            if result:
                self._save_report_to_db(result, now_time, **kwargs)
            else:
                logger.warning(f"Отчёт не был создан: {serv_obj_id}")

        except Exception as e:
            logger.error(f"Ошибка в создании отчёта для задачи {serv_obj_id}: {e}")

    def starter_task(self, **kwargs) -> None:
        """Запускает задачу в отдельном потоке."""
        stop_event = Event()
        serv_obj_id = kwargs['serv_obj_id']

        def task_logic():
            self.all_tasks[serv_obj_id] = kwargs
            while not stop_event.is_set():
                now_time = self._get_now_time()
                if kwargs['subscription_start'] < now_time < kwargs['subscription_end']:
                    self.make_report(now_time, **kwargs)
                else:
                    logger.info(f"Задача {serv_obj_id} завершена.")
                    break
                time.sleep(1)

            self.all_tasks.pop(serv_obj_id, None)
            logger.info(f"Задача {serv_obj_id} завершена и удалена.")

        thread = Thread(target=task_logic, name=f"Task-{serv_obj_id}", daemon=True)
        self.task_registry[serv_obj_id] = {'thread': thread, 'stop_event': stop_event}
        thread.start()

