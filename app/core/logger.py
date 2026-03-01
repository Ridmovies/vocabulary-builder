import logging

from app.core.config import settings


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("app")

    # Уровень логирования
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # Запрещаем проброс в root (иначе будут дубли через uvicorn)
    logger.propagate = False

    # Добавляем handler только один раз
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger


logger = setup_logger()