"""
logger

Этот файл отвечает за логирование в приложении.

Что он делает:
- задаёт единый формат логов;
- выводит логи в консоль;
- сохраняет логи в файл;
- даёт удобный logger, который можно импортировать в любом модуле.

Зачем это нужно:
- проще отлаживать приложение;
- видно, что происходит на каждом этапе;
- удобно искать ошибки в API, сервисах и работе с БД.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from app.core.config import settings


def setup_logging() -> None:
    """
    Настраивает глобальное логирование приложения.

    Функция:
    - создаёт папку для логов;
    - настраивает формат сообщений;
    - добавляет обработчики для консоли и файла;
    - предотвращает дублирование хендлеров.
    """

    log_dir = settings.base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    log_format = (
        "%(asctime)s | %(levelname)s | %(name)s | "
        "%(filename)s:%(lineno)d | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # --- Проверяем, чтобы не добавить хендлеры повторно ---
    has_console = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
    has_file = any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers)

    # --- Консоль ---
    if not has_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # --- Файл ---
    if not has_file:
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # --- Настройка логгеров uvicorn ---
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)

    # access-логи часто шумные → можно приглушить
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# Удобный логгер для приложения
logger = logging.getLogger("tracker")