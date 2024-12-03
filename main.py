import time
from datetime import datetime
from my_logger import logger
from data_base import crud
from tasks import task_collector
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="TaskWorker")
task_generator = task_collector.TaskGenerator()

while True:
    now_time = datetime.now()
    all_unic_tasks = task_generator.get_unic_all_tasks()

    try:
        all_serv = crud.get_actual_serv_two(now_time)
        logger.info(f"полученны сервисы на сейчас {now_time}, сервисы {[i.serv_obj_id for i in all_serv]}")
    except Exception as e:
        logger.error(f"Не получилось получить данные из БД_2 {e}")
    else:
        for serv in all_serv:
            if serv.serv_obj_id not in all_unic_tasks:
                # Передаём задачу в пул потоков
                executor.submit(
                        task_generator.starter_task,
                        serv_obj_id = serv.serv_obj_id, 
                        serv_obj_sys_mon_id = serv.serv_obj_sys_mon_id, 
                        info_obj_serv_id = serv.info_obj_serv_id, 
                        subscription_start = serv.subscription_start, 
                        subscription_end = serv.subscription_end, 
                        tel_num_user = serv.tel_num_user, 
                        service_counter = serv.service_counter, 
                        stealth_type = serv.stealth_type, 
                        monitoring_sys = serv.monitoring_sys, 
                        sys_id_obj = serv.sys_id_obj, 
                        sys_login = serv.sys_login, 
                        sys_password = serv.sys_password 
                        )

    time.sleep(20)



# now_time = datetime.now()
# all_serv = crud.get_actual_serv_two(now_time)
# for i in all_serv:
#
#     print(i.serv_)
