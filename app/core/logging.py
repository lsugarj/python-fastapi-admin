import os
import json
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import re
from app.core.config import get_settings
from app.core.context import get_trace_id

logging_config = get_settings().logging


# =========================
# JSON Formatter
# =========================
class JsonFormatter(logging.Formatter):
    ALLOWED_FIELDS = {
        "method",
        "path",
        "status",
        "duration_ms",
        "client_ip",
        "user_id",
    }

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": get_trace_id(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }

        # 只保留你关心的字段
        for key in self.ALLOWED_FIELDS:
            if hasattr(record, key):
                log[key] = getattr(record, key)

        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, ensure_ascii=False)


# =========================
# 时间 + 大小 双切割 Handler
# =========================
class SizeAndTimeRotatingHandler(TimedRotatingFileHandler):
    def __init__(self, filename, max_bytes, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.max_bytes = max_bytes

    def shouldRollover(self, record):
        # 时间触发
        if super().shouldRollover(record):
            return 1

        # 大小触发
        if self.stream is None:
            self.stream = self._open()

        if self.stream.tell() >= self.max_bytes:
            return 1

        return 0


def _parse_size(size: str) -> int:
    """
    支持：
    10KB / 50MB / 1GB
    """
    size = size.strip().upper()
    match = re.match(r"^(\d+)(KB|MB|GB)?$", size)

    if not match:
        raise ValueError(f"Invalid size format: {size}")

    number, unit = match.groups()
    number = int(number)

    if unit == "KB":
        return number * 1024
    elif unit == "MB":
        return number * 1024 * 1024
    elif unit == "GB":
        return number * 1024 * 1024 * 1024
    else:
        return number


# =========================
# Handler 创建
# =========================
def _build_handler(filename: str, level: int):
    max_bytes = _parse_size(logging_config.max_bytes)
    handler = SizeAndTimeRotatingHandler(
        filename=os.path.join(logging_config.dir, filename),
        when="midnight",
        interval=1,
        backupCount=logging_config.backup_count,
        encoding="utf-8",
        max_bytes=max_bytes,
    )

    handler.setLevel(level)
    handler.setFormatter(JsonFormatter())
    return handler


# =========================
# 初始化日志系统
# =========================
def init_logging():
    # 创建日志目录
    os.makedirs(logging_config.dir, exist_ok=True)
    # 定义handlers
    logging.root.handlers = []
    # app 日志
    app_handler = _build_handler("app.log", logging.INFO)

    # error 日志
    error_handler = _build_handler("error.log", logging.ERROR)

    # console（容器推荐）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())

    logging.basicConfig(
        level=logging.INFO,
        handlers=[app_handler, error_handler, console_handler],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)