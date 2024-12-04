from datetime import datetime
import time
from subprocess import call
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
        """
        Возвращает текущее время.
        """
        return datetime.now()



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
            sys_password,
            now_time
                    ):
        "Какой отчёт выполнять в какое время"
        if service_counter == 0:
            # выполнять отчёт с интервалом через 5 минут
            logger.info(f"Начался выполнятся мгновенный отчёт для задачи {serv_obj_id}")
            result = " "
            try:
                if monitoring_sys == 1:
                    glonas_report = GlonassReport(str(sys_login), str(sys_password), GLONASS_BASED_ADRESS)
                    if info_obj_serv_id == 2:
                        result = glonas_report.get_now_serv_fuel_up_down(sys_id_obj)
                        logger.info(f"Отчёт по {serv_obj_id} {result}")

            except Exception as e:
                logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {serv_obj_id} {e}")
            else:
                try:
                    from information_services_backend.data_base import crud

                    monitoring_sys_name = crud.get_sys_mon_name(monitoring_sys)
                    obj_name = crud.get_obj_name(serv_obj_sys_mon_id)
                    cl_data = crud.get_client_name(sys_login,sys_password)
                    crud.add_report_to_three(
                            time_event=now_time,
                            id_serv_subscription=serv_obj_id, # 'ID подписки'
                            processing_status=0, # 'Статус обработки'
                            monitoring_system=monitoring_sys_name, # 'Система мониторинга' --- -
                            object_name=obj_name, # 'Имя объекта мониторинга' --- -
                            client_name="Максим", # 'Имя клиента' --- - 
                            it_name="Максим", # 'Имя фамилия ИТ специалиста' ---
                            necessary_treatment=stealth_type, # 'Нужна ли обработка IT специали'
                            result=result 
                    )
                    logger.info(f"Отчёт отправился в БД_3 {serv_obj_id} {result} программа засыпает")

                except Exception as e:
                    logger.error(f"НЕ удалось отправить данные в БД {serv_obj_id} {e}")

            finally:
                time.sleep(300)


        elif service_counter == 1:
            # выполнять отчёт каждый день в 09:00-09:05
            if now_time.hour == 9 and now_time.minute in range(0, 6):
                logger.info(f"Выполняется ежедневный отчёт для задачи {serv_obj_id}")
                if monitoring_sys == 1:
                    glonas_report = GlonassReport(str(sys_login), str(sys_password), GLONASS_BASED_ADRESS)
                    try:
                        if info_obj_serv_id == 3: # информация по расходу за предыдущий день
                            result = glonas_report.get_yest_serv_fuel_flow(sys_id_obj)
                            logger.info(f"Отчёт по {serv_obj_id} {result}, программа засыпает")

                        if info_obj_serv_id == 2: # информация по сливам и заправкам за предыдущий день
                            result = glonas_report.get_yest_serv_fuel_up_down(sys_id_obj)
                            logger.info(f"Отчёт по {serv_obj_id} {result}, программа засыпает")

                    except Exception as e:
                        logger.error(f"НЕ УДАЛОСЬ ВЫПОЛНИТЬ ОТЧЁТ {serv_obj_id} {e}")
                # Здесь можно добавить код для выполнения отчета
                time.sleep(60)  # Ждем минуту, чтобы не выполнять отчет несколько раз в течение одной минуты
            
        elif service_counter == 2:
            # выполнять отчёт раз в неделю по понедельникам
            if now_time.weekday() == 0 and now_time.hour == 0 and now_time.minute == 0:
                logger.info(f"Выполняется еженедельный отчёт для задачи {serv_obj_id}")

                # Здесь можно добавить код для выполнения отчета
                time.sleep(60 * 60 * 24)  # Ждем сутки, чтобы не выполнять отчет несколько раз в течение недели

        elif service_counter == 3:
            # выполнять отчёт раз в месяц каждого первого числа
            if now_time.day == 1 and now_time.hour == 0 and now_time.minute == 0:
                logger.info(f"Выполняется ежемесячный отчёт для задачи {serv_obj_id}")

                # Здесь можно добавить код для выполнения отчета
                time.sleep(60 * 60 * 24)  # Ждем сутки, чтобы не выполнять отчет несколько раз в течение месяца

    def get_unic_all_tasks(self):
        return {task["serv_obj_id"] for task in self.all_tasks}

    def starter_task(
            self,
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
            sys_password
            ):
        """
        Запускает задачу, если она находится в интервале времени, и удаляет её после завершения.
            serv_obj_id, - ИД подписки
            serv_obj_sys_mon_id, - Внутренний ИД объекта БД_2
            info_obj_serv_id, - Имя сервиса
            subscription_start, - Время начала подписки
            subscription_end, - Время окончания подписки
            tel_num_user, - Телефонный номер с которого была созд. услуга
            service_counter, - Тип форм.отчётов:
                0-мгновенно(интервал 5мин). 
                1-раз в день. 
                2-раз в неделю. 
                3-раз в месяц
            stealth_type, - Тип отправок:
                0 - автоматическая.
                1 - с проверкой.
            monitoring_sys, - Система мониторинга
            sys_id_obj, - Ид объекта в системе мониторинга
            sys_login, - Логин пользователя
            sys_password - Пароль пользователя
        """

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
                self.make_report(serv_obj_id, serv_obj_sys_mon_id, info_obj_serv_id, subscription_start, subscription_end, tel_num_user, service_counter, stealth_type, monitoring_sys, sys_id_obj, sys_login, sys_password, now_time)

            else:
                logger.info(f"Задача {serv_obj_id} завершена или вышла за границы времени.")
                # Удаляем задачу из списка задач
                self.all_tasks = [task for task in self.all_tasks if task["serv_obj_id"] != serv_obj_id]
                logger.info(f'Задача {serv_obj_id} завершена и удалена из коллектора задач, текущее время {now_time}')
                break

            time.sleep(1)

