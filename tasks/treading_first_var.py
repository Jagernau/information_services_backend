"""
Перераспределение задач между потоками 1
"""
import logging
from queue import Queue
from threading import Thread, Lock
import time

# Настройка логирования
logging.basicConfig(
    filename="task_manager.log",  # Имя файла для логов
    filemode="a",                 # Режим записи: 'a' - добавлять, 'w' - перезаписать
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO            # Уровень логирования: INFO, DEBUG, ERROR и т.д.
)

class TaskWorker(Thread):
    def __init__(self, thread_id, task_queue, active_tasks, lock):
        super().__init__()
        self.thread_id = thread_id
        self.task_queue = task_queue
        self.active_tasks = active_tasks
        self.lock = lock

    def execute_task(self, task):
        """Выполнение задачи."""
        logging.info(f"[THREAD-{self.thread_id}] Начало выполнения задачи: {task['id']}")
        time.sleep(task.get('duration', 1))  # Симуляция выполнения
        logging.info(f"[THREAD-{self.thread_id}] Завершение задачи: {task['id']}")

    def run(self):
        while True:
            try:
                task = self.task_queue.get(timeout=1)  # Ожидание задачи из очереди
            except Exception:
                # Если задач больше нет, завершаем поток
                with self.lock:
                    if not any(self.active_tasks.values()):
                        logging.info(f"[THREAD-{self.thread_id}] Завершение потока.")
                        break
                continue

            # Выполняем задачу
            self.execute_task(task)

            # Удаляем задачу из активных, если она ещё там
            with self.lock:
                if task in self.active_tasks[self.thread_id]:
                    self.active_tasks[self.thread_id].remove(task)
            self.task_queue.task_done()

class TaskManager:
    def __init__(self, max_tasks_per_thread=20):
        self.max_tasks_per_thread = max_tasks_per_thread
        self.task_queue = Queue()
        self.active_tasks = {}
        self.lock = Lock()
        self.threads = []

    def distribute_tasks(self, tasks):
        """Распределение задач по потокам."""
        for task in tasks:
            self.task_queue.put(task)

        thread_id = 0
        while not self.task_queue.empty():
            with self.lock:
                if len(self.threads) <= thread_id or not self.threads[thread_id].is_alive():
                    self.active_tasks[thread_id] = []
                    worker = TaskWorker(thread_id, self.task_queue, self.active_tasks, self.lock)
                    self.threads.append(worker)
                    worker.start()
                if len(self.active_tasks[thread_id]) < self.max_tasks_per_thread:
                    task = self.task_queue.get()
                    self.active_tasks[thread_id].append(task)
                else:
                    thread_id += 1

    def rebalance_tasks(self):
        """Перераспределение задач между потоками."""
        with self.lock:
            all_tasks = [task for tasks in self.active_tasks.values() for task in tasks]
            self.task_queue.queue.clear()
            for task in all_tasks:
                self.task_queue.put(task)
            self.active_tasks.clear()
        self.distribute_tasks([])

# Пример использования
if __name__ == "__main__":
    manager = TaskManager(max_tasks_per_thread=20)

    # Пример списка задач
    tasks = [{"id": i, "duration": 2} for i in range(50)]

    # Распределение задач
    logging.info("Начало распределения задач.")
    manager.distribute_tasks(tasks)
    logging.info("Все задачи распределены.")

    # Ожидание завершения всех потоков
    for thread in manager.threads:
        thread.join()
    logging.info("Все потоки завершены.")

