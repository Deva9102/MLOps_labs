from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# Directory where log files will be stored
LOG_DIR = Path("logs")
# create logs
LOG_DIR.mkdir(exist_ok=True)  

class JsonFormatter(logging.Formatter):
    """
    Custom formatter that outputs each log record as a JSON object.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Convert a LogRecord into a JSON string.
        """
        # Basic fields we want in the log line
        log_record = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        builtin_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
        }

        for key, value in record.__dict__.items():
            if key.startswith("_"):
                continue
            if key in builtin_fields:
                continue
            log_record[key] = value

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Return a compact JSON string
        return json.dumps(log_record, ensure_ascii=False)


def configure_logging() -> logging.Logger:
    """
    Configure and return the main logger for the dataset quality checker.
    """
    logger = logging.getLogger("dq_logger")

    if logger.handlers:
        return logger

    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    logger.setLevel(log_level)
    logger.propagate = False
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)

    file_handler = TimedRotatingFileHandler(
        LOG_DIR / "data_quality.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JsonFormatter())

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.info("Logging configured", extra={"component": "logging_setup"})

    return logger
