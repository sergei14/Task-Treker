"""
logger.py

Файл отвечает за единое логирование backend-приложения:
- выводит сообщения в консоль;
- сохраняет логи в файл backend/logs/app.log;
- ограничивает размер файла логов и создаёт резервные копии;
- настраивает уровень логирования из config.py;
- предоставляет общий logger для остальных модулей приложения.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from app.core.config import settings


LOGGER_NAME = "tracker"
LOG_FILE_NAME = "app.log"
LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | "
    "%(filename)s:%(lineno)d | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    log_file = settings.get_logs_path() / LOG_FILE_NAME

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    app_logger = logging.getLogger(LOGGER_NAME)
    app_logger.setLevel(log_level)
    app_logger.propagate = False

    if not getattr(app_logger, "_configured", False):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        app_logger.addHandler(console_handler)
        app_logger.addHandler(file_handler)

        setattr(app_logger, "_configured", True)

    for handler in app_logger.handlers:
        handler.setLevel(log_level)
        handler.setFormatter(formatter)

    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger(LOGGER_NAME)