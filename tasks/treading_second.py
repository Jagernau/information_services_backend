"""
Тестирование перераспределения задач между потоками
"""
import logging
import threading
import time
from datetime import datetime, timedelta
from queue import Queue


class Task:
    def __init__(self, id_task, execution_time, start_time, end_time):
        self.id_task = id_task
        self.execution_time = execution_time
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f"Task({self.id_task}, {self.execution_time}, {self.start_time}, {self.end_time})"


class TaskManager:
    def __init__(self, max_tasks_per_thread=20):
        self.max_tasks_per_thread = max_tasks_per_thread
        self.tasks_queue = Queue()
        self.threads = []
        self.thread_tasks = {}
        self.lock = threading.Lock()

    def add_task(self, task):
        """
        Добавляет задачу в общую очередь.
        """
        self.tasks_queue.put(task)
        logging.info(f"Задача {task.id_task} добавлена в очередь.")

    def _process_task(self, task, thread_id):
        """
        Обрабатывает задачу.
        """
        logging.info(f"[THREAD-{thread_id}] Начало выполнения задачи: {task.id_task}")
        time.sleep(task.execution_time)
        logging.info(f"[THREAD-{thread_id}] Завершение задачи: {task.id_task}")

        # Удаляем задачу из активных задач
        with self.lock:
            self.thread_tasks[thread_id].remove(task)

    def _worker(self, thread_id):
        """
        Основной метод потока, обрабатывающий задачи.
        """
        with self.lock:
            self.thread_tasks[thread_id] = []

        while True:
            with self.lock:
                if len(self.thread_tasks[thread_id]) < self.max_tasks_per_thread and not self.tasks_queue.empty():
                    task = self.tasks_queue.get()
                    self.thread_tasks[thread_id].append(task)
                    threading.Thread(target=self._process_task, args=(task, thread_id)).start()

            # Перераспределение задач между потоками
            with self.lock:
                for t_id, t_tasks in self.thread_tasks.items():
                    if len(t_tasks) < self.max_tasks_per_thread:
                        for _ in range(len(t_tasks), self.max_tasks_per_thread):
                            if not self.tasks_queue.empty():
                                task = self.tasks_queue.get()
                                self.thread_tasks[t_id].append(task)
                                threading.Thread(target=self._process_task, args=(task, t_id)).start()

            time.sleep(1)

    def start_threads(self, num_threads):
        """
        Запускает заданное количество потоков.
        """
        for thread_id in range(num_threads):
            thread = threading.Thread(target=self._worker, args=(thread_id,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
            logging.info(f"[THREAD-{thread_id}] Запущен.")

