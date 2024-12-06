# tasks/task_collector.py
from datetime import datetime
import time
from threading import Thread, Event
from subprocess import call
import sys
import random

sys.path.append('../')
from information_services_backend.my_logger import logger
from information_services_backend.generating_reports.glonass_reports import GlonassReport
from information_services_backend.config import GLONASS_BASED_ADRESS

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

    def make_report(self, *args, **kwargs):
        """
        Реализация make_report как есть.
        """
        now_time = self._get_now_time()
        serv_obj_id = kwargs['serv_obj_id']
        service_counter = kwargs['service_counter']
        monitoring_sys = kwargs['monitoring_sys']
        info_obj_serv_id = kwargs['info_obj_serv_id']
        sys_login = kwargs['sys_login']
        sys_password = kwargs['sys_password']
        sys_id_obj = kwargs['sys_id_obj']
        stealth_type = kwargs['stealth_type']
        serv_obj_sys_mon_id = kwargs['serv_obj_sys_mon_id']

        if service_counter == 0:
            # выполнять отчёт с интервалом через 5 минут
            logger.info(f"Начался выполнятся мгновенный отчёт для задачи {serv_obj_id}")
            result = None
            try:
                if monitoring_sys == 1:
                    glonas_report = GlonassReport(str(sys_login), str(sys_password), GLONASS_BASED_ADRESS)
                    if info_obj_serv_id == 2:
                        time.sleep(random.uniform(0.9, 1.8))
                        result = glonas_report.get_now_serv_fuel_up_down(sys_id_obj)
                        logger.info(f"Отчёт по {serv_obj_id} {result}")

            except Exception as e:
                logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {serv_obj_id} {e}")
            else:
                try:
                    if result:
                        from information_services_backend.data_base import crud

                        monitoring_sys_name = crud.get_sys_mon_name(monitoring_sys)
                        obj_name = crud.get_obj_name(serv_obj_sys_mon_id)
                        cl_data = crud.get_client_name(sys_login,sys_password)
                        crud.add_report_to_three(
                                time_event=now_time,
                                id_serv_subscription=serv_obj_id,
                                processing_status=0,
                                monitoring_system=monitoring_sys_name,
                                object_name=obj_name,
                                client_name=cl_data[0],
                                it_name=cl_data[1],
                                necessary_treatment=stealth_type,
                                result=result,
                                login=sys_login
                        )
                        logger.info(f"Отчёт отправился в БД_3 {serv_obj_id} {result} программа засыпает")

                except Exception as e:
                    logger.error(f"НЕ удалось отправить данные в БД {serv_obj_id} {e}")

            finally:
                logger.info(f"Программа засыпает {serv_obj_id}")
                time.sleep(300)


        elif service_counter == 1:
            result = None
            # выполнять отчёт каждый день в 09:00-09:05
            if now_time.hour == 9 and now_time.minute in range(0, 6):
                logger.info(f"Выполняется ежедневный отчёт для задачи {serv_obj_id}")
                if monitoring_sys == 1:
                    glonas_report = GlonassReport(str(sys_login), str(sys_password), GLONASS_BASED_ADRESS)
                    try:
                        if info_obj_serv_id == 3: # информация по расходу за предыдущий день
                            time.sleep(random.uniform(0.9, 1.8))
                            result = glonas_report.get_yest_serv_fuel_flow(sys_id_obj)
                            logger.info(f"Отчёт по {serv_obj_id} {result}")

                        if info_obj_serv_id == 2: # информация по сливам и заправкам за предыдущий день
                            time.sleep(random.uniform(0.9, 1.8))
                            result = glonas_report.get_yest_serv_fuel_up_down(sys_id_obj)
                            logger.info(f"Отчёт по {serv_obj_id} {result}")

                    except Exception as e:
                        logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {serv_obj_id} {e}")
                # Здесь можно добавить код для выполнения отчета
                    else:
                        try:
                            if result:
                                from information_services_backend.data_base import crud

                                monitoring_sys_name = crud.get_sys_mon_name(monitoring_sys)
                                obj_name = crud.get_obj_name(serv_obj_sys_mon_id)
                                cl_data = crud.get_client_name(sys_login,sys_password)
                                crud.add_report_to_three(
                                        time_event=now_time,
                                        id_serv_subscription=serv_obj_id,
                                        processing_status=0,
                                        monitoring_system=monitoring_sys_name,
                                        object_name=obj_name,
                                        client_name=cl_data[0],
                                        it_name=cl_data[1],
                                        necessary_treatment=stealth_type,
                                        result=result,
                                        login=sys_login
                                )
                                logger.info(f"Отчёт отправился в БД_3 {serv_obj_id} {result} программа засыпает")

                        except Exception as e:
                            logger.error(f"НЕ удалось отправить данные в БД {serv_obj_id} {e}")
                    finally:
                        time.sleep(60)  # Ждем минуту, чтобы не выполнять отчет несколько раз в течение одной минуты
            
        elif service_counter == 2:
            result = None
            # выполнять отчёт раз в неделю по понедельникам
            if now_time.weekday() == 0 and now_time.hour == 0 and now_time.minute == 0:
                logger.info(f"Выполняется еженедельный отчёт для задачи {serv_obj_id}")
                if monitoring_sys == 1:
                    glonas_report = GlonassReport(str(sys_login), str(sys_password), GLONASS_BASED_ADRESS)
                    try:
                        if info_obj_serv_id == 3: # информация по расходу за предыдущий день
                            time.sleep(random.uniform(0.9, 1.8))
                            result = glonas_report.get_yest_serv_fuel_flow(sys_id_obj)
                            logger.info(f"Отчёт по {serv_obj_id} {result}")

                        if info_obj_serv_id == 2: # информация по сливам и заправкам за предыдущий день
                            time.sleep(random.uniform(0.9, 1.8))
                            result = glonas_report.get_yest_serv_fuel_up_down(sys_id_obj)
                            logger.info(f"Отчёт по {serv_obj_id} {result}")

                    except Exception as e:
                        logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {serv_obj_id} {e}")
                # Здесь можно добавить код для выполнения отчета
                    else:
                        try:
                            if result:
                                from information_services_backend.data_base import crud

                                monitoring_sys_name = crud.get_sys_mon_name(monitoring_sys)
                                obj_name = crud.get_obj_name(serv_obj_sys_mon_id)
                                cl_data = crud.get_client_name(sys_login,sys_password)
                                crud.add_report_to_three(
                                        time_event=now_time,
                                        id_serv_subscription=serv_obj_id,
                                        processing_status=0,
                                        monitoring_system=monitoring_sys_name,
                                        object_name=obj_name,
                                        client_name=cl_data[0],
                                        it_name=cl_data[1],
                                        necessary_treatment=stealth_type,
                                        result=result,
                                        login=sys_login
                                )
                                logger.info(f"Отчёт отправился в БД_3 {serv_obj_id} {result} программа засыпает")

                        except Exception as e:
                            logger.error(f"НЕ удалось отправить данные в БД {serv_obj_id} {e}")
                    finally:
                        time.sleep(60 * 60 * 24)  # Ждем сутки, чтобы не выполнять отчет несколько раз в течение недели

        elif service_counter == 3:
            result = None
            # выполнять отчёт раз в месяц каждого первого числа
            if now_time.day == 1 and now_time.hour == 0 and now_time.minute == 0:
                logger.info(f"Выполняется ежемесячный отчёт для задачи {serv_obj_id}")
                if monitoring_sys == 1:
                    glonas_report = GlonassReport(str(sys_login), str(sys_password), GLONASS_BASED_ADRESS)
                    try:
                        if info_obj_serv_id == 3: # информация по расходу за предыдущий день
                            time.sleep(random.uniform(0.9, 1.8))
                            result = glonas_report.get_yest_serv_fuel_flow(sys_id_obj)
                            logger.info(f"Отчёт по {serv_obj_id} {result}")

                        if info_obj_serv_id == 2: # информация по сливам и заправкам за предыдущий день
                            time.sleep(random.uniform(0.9, 1.8))
                            result = glonas_report.get_yest_serv_fuel_up_down(sys_id_obj)
                            logger.info(f"Отчёт по {serv_obj_id} {result}")

                    except Exception as e:
                        logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {serv_obj_id} {e}")
                # Здесь можно добавить код для выполнения отчета
                    else:
                        try:
                            if result:
                                from information_services_backend.data_base import crud

                                monitoring_sys_name = crud.get_sys_mon_name(monitoring_sys)
                                obj_name = crud.get_obj_name(serv_obj_sys_mon_id)
                                cl_data = crud.get_client_name(sys_login,sys_password)
                                crud.add_report_to_three(
                                        time_event=now_time,
                                        id_serv_subscription=serv_obj_id,
                                        processing_status=0,
                                        monitoring_system=monitoring_sys_name,
                                        object_name=obj_name,
                                        client_name=cl_data[0],
                                        it_name=cl_data[1],
                                        necessary_treatment=stealth_type,
                                        result=result,
                                        login=sys_login
                                )
                                logger.info(f"Отчёт отправился в БД_3 {serv_obj_id} {result} программа засыпает")

                        except Exception as e:
                            logger.error(f"НЕ удалось отправить данные в БД {serv_obj_id} {e}")
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
                    self.make_report(now_time=now_time, **kwargs)
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
