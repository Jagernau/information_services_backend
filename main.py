# new_main.py
"""
Основной асинхронный запуск программы
"""

import asyncio
from datetime import datetime
from my_logger import logger
from data_base.crud import CrudService
from tasks.new_task_collector import TaskGenerator

task_generator = TaskGenerator()


async def main():
    """
    Основной асинхронный цикл программы.
    """
    while True:
        now_time = datetime.now()
        all_unic_tasks = task_generator.get_unic_all_tasks()

        try:
            # Получаем актуальные сервисы из базы данных
            all_serv = await CrudService.get_actual_serv_two(now_time)
            logger.info(f"Получены сервисы на {now_time}, сервисы {[i.serv_obj_id for i in all_serv]}")
        except Exception as e:
            logger.error(f"Ошибка получения данных из БД: {e}")
        else:
            # Добавление новых задач
            for serv in all_serv:
                if serv.serv_obj_id not in all_unic_tasks:
                    asyncio.create_task(task_generator.starter_task(**vars(serv)))

            # Остановка неактуальных задач
            active_tasks = task_generator.get_unic_all_tasks()
            db_task_ids = {serv.serv_obj_id for serv in all_serv}
            tasks_to_stop = active_tasks - db_task_ids
            for task_id in tasks_to_stop:
                await task_generator.stop_task(task_id)

        await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())

