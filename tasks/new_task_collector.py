# tasks/task_collector.py
import asyncio
from datetime import datetime, timedelta
from my_logger import logger
from generating_reports.glonass_reports import GlonassReport
from data_base.crud import CrudService
from config import GLONASS_BASED_ADRESS


class TaskGenerator:
    """
    Асинхронный генератор задач с проверкой времени выполнения.
    """

    def __init__(self):
        self.task_registry = {}  # Словарь для отслеживания задач

    def get_unic_all_tasks(self):
        """
        Возвращает текущие активные задачи.
        """
        return set(self.task_registry.keys())

    async def stop_task(self, serv_obj_id):
        """
        Асинхронно завершает задачу и удаляет её из реестра.
        """
        if serv_obj_id in self.task_registry:
            logger.info(f"Остановка задачи {serv_obj_id}")
            self.task_registry[serv_obj_id]['stop_event'].set()
            await self.task_registry[serv_obj_id]['task']  # Ожидание завершения задачи
            del self.task_registry[serv_obj_id]
            logger.info(f"Задача {serv_obj_id} остановлена.")

    async def _make_report(self, **kwargs):
        """
        Асинхронно выполняет генерацию отчёта.
        """
        try:
            glonas_report = GlonassReport(kwargs['sys_login'], kwargs['sys_password'], GLONASS_BASED_ADRESS)
            now_time = datetime.now()
            result = None

            if kwargs['service_counter'] == 0:  # Отчёт раз в 5 минут
                logger.info(f"Начался выполнятся мгновенный отчёт для задачи {kwargs['serv_obj_id']}")
                if kwargs["monitoring_sys"] == 1: # glonass
                    if kwargs["info_obj_serv_id"] == 2: # сливы запр
                        result = await glonas_report.get_now_serv_fuel_up_down(kwargs['sys_id_obj'])
                if result:
                    # Добавление отчёта в базу данных
                    monitoring_sys_name = await CrudService.get_sys_mon_name(kwargs['monitoring_sys'])
                    obj_name = await CrudService.get_obj_name(kwargs['serv_obj_sys_mon_id'])
                    cl_data = await CrudService.get_client_name(kwargs['sys_login'], kwargs['sys_password'])
                    await CrudService.add_report_to_three(
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
                    logger.info(f"Отчёт добавлен в БД для задачи {kwargs['serv_obj_id']}: {result} Задача засыпает")
                    await asyncio.sleep(5 * 60)
                else:
                    logger.error(f"Отчёт не пришёл, задача засыпает")
                    await asyncio.sleep(5 * 60)


            elif kwargs['service_counter'] == 1:  # Ежедневный отчёт
                if now_time.hour == 9 and now_time.minute in range(0, 6):
                    logger.info(f"Выполняется ежедневный отчёт для задачи {kwargs['serv_obj_id']}")

                if kwargs["monitoring_sys"] == 1: # glonass
                    if kwargs["info_obj_serv_id"] == 2: # сливы запр
                        result = await glonas_report.get_yest_serv_fuel_up_down(kwargs['sys_id_obj'])
                    if kwargs["info_obj_serv_id"] == 3: # расходу за предыдущий день
                        result = await glonas_report.get_yest_serv_fuel_flow(kwargs['sys_id_obj'])
                    if result:
                        # Добавление отчёта в базу данных
                        monitoring_sys_name = await CrudService.get_sys_mon_name(kwargs['monitoring_sys'])
                        obj_name = await CrudService.get_obj_name(kwargs['serv_obj_sys_mon_id'])
                        cl_data = await CrudService.get_client_name(kwargs['sys_login'], kwargs['sys_password'])
                        await CrudService.add_report_to_three(
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
                        logger.info(f"Отчёт добавлен в БД для задачи {kwargs['serv_obj_id']}: {result} Задача засыпает")
                        await asyncio.sleep(60)
                    else:
                        logger.error(f"Отчёт не пришёл, задача засыпает")
                        await asyncio.sleep(60)


            elif kwargs['service_counter'] == 2:  # Еженедельный отчёт
                if now_time.weekday() == 0 and now_time.hour == 0 and now_time.minute == 0:
                    logger.info(f"Выполняется еженедельный отчёт для задачи {kwargs['serv_obj_id']}")
                    result = await glonas_report.get_yest_serv_fuel_flow(kwargs['sys_id_obj'])
                    if result:
                        # Добавление отчёта в базу данных
                        monitoring_sys_name = await CrudService.get_sys_mon_name(kwargs['monitoring_sys'])
                        obj_name = await CrudService.get_obj_name(kwargs['serv_obj_sys_mon_id'])
                        cl_data = await CrudService.get_client_name(kwargs['sys_login'], kwargs['sys_password'])
                        await CrudService.add_report_to_three(
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
                        logger.info(f"Отчёт добавлен в БД для задачи {kwargs['serv_obj_id']}: {result} Задача засыпает")
                        await asyncio.sleep(60 * 60 * 24)
                    else:
                        logger.error(f"Отчёт не пришёл, задача засыпает")
                        await asyncio.sleep(60 * 60 * 24)

            elif kwargs['service_counter'] == 3:  # Ежемесячный отчёт
                if now_time.day == 1 and now_time.hour == 0 and now_time.minute == 0:
                    logger.info(f"Выполняется ежемесячный отчёт для задачи {kwargs['serv_obj_id']}")
                    result = await glonas_report.get_yest_serv_fuel_flow(kwargs['sys_id_obj'])
                    if result:
                        # Добавление отчёта в базу данных
                        monitoring_sys_name = await CrudService.get_sys_mon_name(kwargs['monitoring_sys'])
                        obj_name = await CrudService.get_obj_name(kwargs['serv_obj_sys_mon_id'])
                        cl_data = await CrudService.get_client_name(kwargs['sys_login'], kwargs['sys_password'])
                        await CrudService.add_report_to_three(
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
                        logger.info(f"Отчёт добавлен в БД для задачи {kwargs['serv_obj_id']}: {result} Задача засыпает")
                        await asyncio.sleep(60 * 60 * 24)
                    else:
                        logger.error(f"Отчёт не пришёл, задача засыпает")
                        await asyncio.sleep(60 * 60 * 24)

        except Exception as e:
            logger.error(f"Ошибка при генерации отчёта для задачи {kwargs['serv_obj_id']}: {e}")

    async def starter_task(self, **kwargs):
        """
        Асинхронный запуск задачи.
        """
        stop_event = asyncio.Event()
        serv_obj_id = kwargs['serv_obj_id']
        self.task_registry[serv_obj_id] = {'task': None, 'stop_event': stop_event}

        async def task_logic():
            """
            Основная логика выполнения задачи.
            """
            logger.info(f"Запуск задачи {serv_obj_id}")
            while not stop_event.is_set():
                now_time = datetime.now()
                subscription_start = kwargs['subscription_start']
                subscription_end = kwargs['subscription_end']

                if subscription_start < now_time < subscription_end:
                    logger.info(f"Задача {serv_obj_id} активна: текущее время {now_time}")
                    await self._make_report(**kwargs)
                else:
                    logger.info(f"Задача {serv_obj_id} завершена по времени.")
                    break

                await asyncio.sleep(1)  # Интервал между итерациями

            logger.info(f"Задача {serv_obj_id} завершена.")

        self.task_registry[serv_obj_id]['task'] = asyncio.create_task(task_logic())

