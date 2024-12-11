from datetime import datetime
import time
from threading import Thread, Event
import sys
import random

sys.path.append('../')
from information_services_backend.my_logger import logger

class TaskGenerator:
    """
    Генератор задач с проверкой времени выполнения.
    """

    def __init__(self):
        self.all_tasks = {}
        self.task_registry = {}  # Tracks tasks by ID with stop signals

    def _get_now_time(self):
        """
        Возвращает текущее время.
        """
        return datetime.now()

    def get_unic_all_tasks(self):
        return set(self.task_registry.keys())

    def gen_random_num(self):
        return random.uniform(1.2, 3.7)

    def stop_task(self, serv_obj_id):
        """
        Signals a task to stop and waits for it to terminate.
        """
        if serv_obj_id in self.task_registry:
            logger.info(f"Остановка задачи {serv_obj_id}")
            self.task_registry[serv_obj_id]['stop_event'].set()
            self.task_registry[serv_obj_id]['thread'].join()  # Wait for the thread to finish
            del self.task_registry[serv_obj_id]
            logger.info(f"Задача {serv_obj_id} остановлена.")

    def save_data_db_three(self, **kwargs):
        try:
            from information_services_backend.data_base import crud
            monitoring_sys_name = crud.get_sys_mon_name(kwargs['monitoring_sys'])
            obj_name = crud.get_obj_name(kwargs['serv_obj_sys_mon_id'])
            cl_data = crud.get_client_name(kwargs['sys_login'],kwargs['sys_password'])
            crud.add_report_to_three(
                    time_event=kwargs["now_time"],
                    id_serv_subscription=kwargs['serv_obj_id'],
                    processing_status=0,
                    monitoring_system=monitoring_sys_name,
                    object_name=obj_name,
                    client_name=cl_data[0],
                    it_name=cl_data[1],
                    necessary_treatment=kwargs['stealth_type'],
                    result=kwargs["result"],
                    login=kwargs['sys_login']
            )
            logger.info(f"Отчёт отправился в БД_3 {kwargs['serv_obj_id']} {kwargs['result']} программа засыпает")
        except Exception as e:
            logger.error(f"НЕ удалось отправить данные в БД {kwargs['serv_obj_id']} {e}")


    def make_report(self, *args, **kwargs):
        """
        Реализация make_report как есть.
        """
        from tasks.report_manager import ManageReport
        now_time = self._get_now_time()
        kwargs["now_time"] = now_time
        if kwargs["service_counter"] == 0:
            # выполнять отчёт с интервалом через 5 минут
            logger.info(f"Начался выполнятся мгновенный отчёт для задачи {kwargs['serv_obj_id']}")
            result = None
            try:
                with ManageReport(**kwargs) as report:
                    result = report.get_sys_mon_report()
            except Exception as e:
                logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {kwargs['serv_obj_id']} {e}")
            else:
                if result:
                    kwargs["result"] = result
                    self.save_data_db_three(**kwargs)
            finally:
                logger.info(f"Программа засыпает {kwargs['serv_obj_id']}")
                time.sleep(1800)

        elif kwargs['service_counter'] == 1:
            # выполнять отчёт каждый день в 09:00-09:05
            if now_time.hour == 9 and now_time.minute in range(0, 2):
                logger.info(f"Выполняется ежедневный отчёт для задачи {kwargs['serv_obj_id']}")
                result = None
                try:
                    with ManageReport(**kwargs) as report:
                        result = report.get_sys_mon_report()
                except Exception as e:
                    logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {kwargs['serv_obj_id']} {e}")
                else:
                    if result:
                        kwargs["result"] = result
                        self.save_data_db_three(**kwargs)
                finally:
                    time.sleep(60)  # Ждем минуту, чтобы не выполнять отчет несколько раз в течение одной минуты
            
        elif kwargs['service_counter'] == 2:
            # выполнять отчёт раз в неделю по понедельникам
            if now_time.weekday() == 0 and now_time.hour == 0 and now_time.minute == 0:
                logger.info(f"Выполняется еженедельный отчёт для задачи {kwargs['serv_obj_id']}")
                result = None
                try:
                    with ManageReport(**kwargs) as report:
                        result = report.get_sys_mon_report()
                except Exception as e:
                    logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {kwargs['serv_obj_id']} {e}")
            # Здесь можно добавить код для выполнения отчета
                else:
                    if result:
                        kwargs["result"] = result
                        self.save_data_db_three(**kwargs)
                finally:
                    time.sleep(60 * 60 * 24)  # Ждем сутки, чтобы не выполнять отчет несколько раз в течение недели

        elif kwargs['service_counter'] == 3:
            # выполнять отчёт раз в месяц каждого первого числа
            if now_time.day == 1 and now_time.hour == 0 and now_time.minute == 0:
                logger.info(f"Выполняется ежемесячный отчёт для задачи {kwargs['serv_obj_id']}")
                result = None
                try:
                    with ManageReport(**kwargs) as report:
                        result = report.get_sys_mon_report()
                except Exception as e:
                    logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {kwargs['serv_obj_id']} {e}")
            # Здесь можно добавить код для выполнения отчета
                else:
                    if result:
                        kwargs["result"] = result
                        self.save_data_db_three(**kwargs)
                finally:
                    time.sleep(60 * 60 * 24)  # Ждем сутки, чтобы не выполнять отчет несколько раз в течение недели

    def starter_task(self, **kwargs):
        """
        Starts and manages a task in a thread.
        """
        stop_event = Event()
        serv_obj_id = kwargs['serv_obj_id']

        def task_logic():
            self.all_tasks[serv_obj_id] = kwargs
            while not stop_event.is_set():
                now_time = self._get_now_time()
                subscription_start = kwargs['subscription_start']
                subscription_end = kwargs['subscription_end']

                if subscription_start < now_time < subscription_end:
                    # logger.info(f"Задача {serv_obj_id} работает, текущее время: {now_time}")
                    self.make_report(**kwargs)
                else:
                    logger.info(f"Задача {serv_obj_id} завершена или вышла за границы времени.")
                    break

                time.sleep(1)  # Adjust polling interval as needed

            # Cleanup after task stops
            self.all_tasks.pop(serv_obj_id, None)
            logger.info(f"Задача {serv_obj_id} завершена и удалена из коллектора задач.")

        thread = Thread(target=task_logic, name=f"Task-{serv_obj_id}", daemon=True)
        self.task_registry[serv_obj_id] = {'thread': thread, 'stop_event': stop_event}
        thread.start()
