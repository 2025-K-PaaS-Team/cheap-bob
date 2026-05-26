"""로깅 설정 (main-backend 와 동일 정책)."""

import sys
from pathlib import Path
from loguru._logger import Logger
from loguru import logger
import logging

from app.config.setting import settings


def setup_logging() -> None:
    requested_format = settings.LOG_FORMAT
    forced_json = settings.is_production and requested_format != "json"
    log_format = "json" if forced_json else requested_format

    logger.remove()

    if log_format == "json":
        logger.add(
            sys.stdout,
            format="{message}",
            serialize=True,
            level=settings.LOG_LEVEL,
            enqueue=True,
        )
    else:
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level> | {extra}"
            ),
            level=settings.LOG_LEVEL,
            colorize=True,
            enqueue=True,
        )

    if settings.LOG_FILE_PATH:
        log_path = Path(settings.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            settings.LOG_FILE_PATH,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            compression=settings.LOG_COMPRESSION,
            format="{message}",
            serialize=True,
            level="INFO",
            encoding="utf-8",
            enqueue=True,
        )

    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage(),
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    if forced_json:
        logger.warning(
            "PROD 환경에서 LOG_FORMAT={} 가 지정되어 있어 json 으로 강제 변환했습니다.",
            requested_format,
        )

    logger.info("Logging system initialized with level: {}", settings.LOG_LEVEL)


def get_logger(name: str) -> Logger:
    return logger.bind(logger_name=name)


app_logger = get_logger("app")
