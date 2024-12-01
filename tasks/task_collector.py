from datetime import datetime
import time


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

    def _sort_report(self, type_report):
        "Какой отчёт выполнять"
        if type_report == 0:
            # выполнять отчёт с интервалом через 5 минут
            pass

        if type_report == 1:
            # выполнять отчёт каждый день в 09:00
            pass
        if type_report == 2:
            # выполнять отчёт раз в неделю по понедельникам
            pass
        if type_report == 3:
            # выполнять отчёт раз в месяц каждого первого числа
            pass


    def starter_task(self, id_task, execution_time, start_time, end_time):
        """
        Запускает задачу, если она находится в интервале времени, и удаляет её после завершения.
        """
        # Проверяем уникальность задачи
        unique_tasks = {task["id_task"] for task in self.all_tasks}

        if id_task not in unique_tasks and start_time < self._get_now_time() < end_time:
            while True:
                now_time = self._get_now_time()
                if start_time < now_time < end_time:
                    print(f"Задача {id_task} работает, текущее время: {now_time}")
                else:
                    print(f"Задача {id_task} завершена или вышла за границы времени.")
                    # Удаляем задачу из списка задач
                    self.all_tasks = [task for task in self.all_tasks if task["id_task"] != id_task]
                    break

                time.sleep(5)

