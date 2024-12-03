import asyncio
from datetime import datetime
from my_logger import logger


class TaskCollector:
    def __init__(self):
        self.running_tasks = {}  # Словарь текущих задач {serv_obj_id: asyncio.Task}

    def _get_now_time(self):
        """Получение текущего времени."""
        return datetime.now()

    async def run_task(self, task_data):
        """Запуск задачи."""
        serv_obj_id = task_data.serv_obj_id
        logger.info(f"Задача {serv_obj_id} запущена")

        try:
            while True:
                now_time = self._get_now_time()

                # Проверка времени действия задачи
                if task_data.subscription_start < now_time < task_data.subscription_end:
                    logger.info(f"Задача {serv_obj_id} работает, текущее время: {now_time}")
                    await asyncio.sleep(5)  # Симуляция работы задачи
                else:
                    logger.info(f"Задача {serv_obj_id} завершена.")
                    break
        except Exception as e:
            logger.error(f"Ошибка в задаче {serv_obj_id}: {e}")
        finally:
            # Удаляем задачу из списка выполняющихся
            self.running_tasks.pop(serv_obj_id, None)
            logger.info(f"Задача {serv_obj_id} удалена из списка выполняющихся")

    async def create_and_run_tasks(self, tasks_from_db):
        """Создание и запуск новых задач."""
        for task_data in tasks_from_db:
            if task_data.serv_obj_id not in self.running_tasks:
                # Создаём и запускаем новую задачу
                task = asyncio.create_task(self.run_task(task_data))
                self.running_tasks[task_data.serv_obj_id] = task
                logger.info(f"Создана новая задача: {task_data.serv_obj_id}")

        # Лог выполняющихся задач
        logger.info(f"Текущие задачи: {list(self.running_tasks.keys())}")

