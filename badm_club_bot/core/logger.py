# logger.py
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

LOG_DIR = "logs"
LOG_FILE = "bot.log"
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging(log_level=logging.INFO):
	"""
    Настройка логирования для бота

    Args:
        log_level: Уровень логирования (logging.INFO, logging.DEBUG, etc.)
    """
	# Создаем форматтер
	formatter = logging.Formatter(
		"%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S"
	)

	# Хендлер для файла
	file_handler = RotatingFileHandler(
		filename=os.path.join(LOG_DIR, LOG_FILE),
		maxBytes=5 * 1024 * 1024,  # 5 MB
		backupCount=5,
		encoding="utf-8"
	)
	file_handler.setFormatter(formatter)
	file_handler.setLevel(log_level)

	# Хендлер для консоли
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(formatter)
	console_handler.setLevel(log_level)

	# Настраиваем корневой логгер
	root_logger = logging.getLogger()
	root_logger.setLevel(log_level)

	# Удаляем существующие хендлеры (чтобы избежать дублирования)
	root_logger.handlers.clear()

	# Добавляем хендлеры
	root_logger.addHandler(file_handler)
	root_logger.addHandler(console_handler)

	# Настраиваем уровень логирования для сторонних библиотек
	logging.getLogger("aiogram").setLevel(logging.WARNING)  # Меньше спама от aiogram
	logging.getLogger("asyncio").setLevel(logging.WARNING)

	# Тестовое сообщение
	logging.info("Логирование настроено успешно")
	logging.info(f"Логи сохраняются в: {os.path.join(LOG_DIR, LOG_FILE)}")