import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Создание обработчика для записи в файл
file_handler = logging.FileHandler('log.txt')
file_handler.setLevel(logging.INFO)

# Формат логов с добавлением имени потока
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s')
file_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(file_handler)
