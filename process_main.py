import time
from datetime import datetime
from my_logger import logger
from data_base import crud
from tasks import task_collector
from concurrent.futures import ProcessPoolExecutor

task_generator = task_collector.TaskGenerator()

# Максимальное количество процессов
MAX_PROCESSES = 3
TASKS_PER_PROCESS = 10  # Количество задач в одном процессе


def process_task_group(task_group):
    """Функция для обработки группы задач в отдельном процессе."""
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=5, thread_name_prefix="TaskWorker") as executor:
        for task in task_group:
            executor.submit(
                task_generator.starter_task,
                **task
            )


while True:
    now_time = datetime.now()
    all_unic_tasks = task_generator.get_unic_all_tasks()

    try:
        all_serv = crud.get_actual_serv_two(now_time)
        logger.info(f"полученны сервисы на сейчас {now_time}, сервисы {[i.serv_obj_id for i in all_serv]}")
    except Exception as e:
        logger.error(f"Не получилось получить данные из БД_2 {e}")
    else:
        # Создаём задачи для выполнения
        new_tasks = []
        for serv in all_serv:
            if serv.serv_obj_id not in all_unic_tasks:
                new_tasks.append({
                    'serv_obj_id': serv.serv_obj_id,
                    'serv_obj_sys_mon_id': serv.serv_obj_sys_mon_id,
                    'info_obj_serv_id': serv.info_obj_serv_id,
                    'subscription_start': serv.subscription_start,
                    'subscription_end': serv.subscription_end,
                    'tel_num_user': serv.tel_num_user,
                    'service_counter': serv.service_counter,
                    'stealth_type': serv.stealth_type,
                    'monitoring_sys': serv.monitoring_sys,
                    'sys_id_obj': serv.sys_id_obj,
                    'sys_login': serv.sys_login,
                    'sys_password': serv.sys_password,
                })

        # Разбиваем задачи на группы для выполнения в разных процессах
        task_groups = [new_tasks[i:i + TASKS_PER_PROCESS] for i in range(0, len(new_tasks), TASKS_PER_PROCESS)]

        # Запускаем группы задач в процессах
        with ProcessPoolExecutor(max_workers=MAX_PROCESSES) as process_executor:
            process_executor.map(process_task_group, task_groups)

    time.sleep(10)

