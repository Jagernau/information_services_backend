import asyncio
from datetime import datetime
from my_logger import logger
from data_base import crud
from tasks.asinc_task_collector import TaskCollector

# Инициализация объекта для управления задачами
task_collector = TaskCollector()


async def poll_database():
    """Асинхронный опрос базы данных для получения новых задач."""
    while True:
        now_time = datetime.now()
        logger.info(f"Опрос базы данных на {now_time}")

        try:
            # Получаем актуальные задачи из базы данных
            tasks_from_db = crud.get_actual_serv_two(now_time)
            logger.info(f"Получены сервисы: {[task.serv_obj_id for task in tasks_from_db]}")

            # Создание и запуск новых задач
            await task_collector.create_and_run_tasks(tasks_from_db)
        except Exception as e:
            logger.error(f"Ошибка при опросе базы данных: {e}")

        # Задержка перед следующим опросом
        await asyncio.sleep(10)


async def main():
    """Главная функция для запуска программы."""
    logger.info("Запуск программы")
    await poll_database()


if __name__ == "__main__":
    asyncio.run(main())

