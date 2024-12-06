""" 
Основной Многопоточная работа программы
"""
import time
from datetime import datetime
from my_logger import logger
from data_base import crud
from tasks import new_task_collector
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="TaskWorker")
task_generator = new_task_collector.TaskGenerator()

while True:
    now_time = datetime.now()
    all_unic_tasks = task_generator.get_unic_all_tasks()

    try:
        all_serv = crud.get_actual_serv_two(now_time)
        logger.info(f"полученны сервисы на сейчас {now_time}, сервисы {[i.serv_obj_id for i in all_serv]}")
    except Exception as e:
        logger.error(f"Не получилось получить данные из БД_2 {e}")
    else:
        # Add or update tasks
        for serv in all_serv:
            if serv.serv_obj_id not in all_unic_tasks:
                executor.submit(task_generator.starter_task, **vars(serv))

        # Stop tasks that are no longer in the database
        active_tasks = task_generator.get_unic_all_tasks()
        db_task_ids = {serv.serv_obj_id for serv in all_serv}
        tasks_to_stop = active_tasks - db_task_ids
        for task_id in tasks_to_stop:
            task_generator.stop_task(task_id)

    time.sleep(600)
