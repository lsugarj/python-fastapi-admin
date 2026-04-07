import json
import logging
from logging.handlers import TimedRotatingFileHandler

import pytest

from app.core.context import set_trace_id
import app.core.logging as core_logging


def test_parse_size():
    assert core_logging._parse_size("10KB") == 10 * 1024
    assert core_logging._parse_size("50MB") == 50 * 1024 * 1024
    assert core_logging._parse_size("1GB") == 1 * 1024 * 1024 * 1024
    assert core_logging._parse_size("123") == 123


def test_parse_size_invalid():
    with pytest.raises(ValueError):
        core_logging._parse_size("50 MB")


def test_json_formatter_includes_trace_and_allowed_fields():
    set_trace_id("tid-123")
    formatter = core_logging.JsonFormatter()

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    record.method = "GET"
    record.path = "/x"
    record.status = 200
    record.duration_ms = 12.34
    record.client_ip = "127.0.0.1"
    record.user_id = 7
    record.not_allowed = "nope"

    payload = json.loads(formatter.format(record))
    assert payload["message"] == "hello world"
    assert payload["trace_id"] == "tid-123"
    assert payload["method"] == "GET"
    assert payload["path"] == "/x"
    assert payload["status"] == 200
    assert payload["duration_ms"] == 12.34
    assert payload["client_ip"] == "127.0.0.1"
    assert payload["user_id"] == 7
    assert "not_allowed" not in payload


def test_size_and_time_rotating_handler_rolls_on_size(tmp_path, monkeypatch):
    monkeypatch.setattr(TimedRotatingFileHandler, "shouldRollover", lambda self, record: 0)

    handler = core_logging.SizeAndTimeRotatingHandler(
        filename=str(tmp_path / "x.log"),
        when="midnight",
        interval=1,
        backupCount=1,
        encoding="utf-8",
        max_bytes=10,
    )
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="x",
        args=(),
        exc_info=None,
    )

    handler.stream.write("0123456789012345")
    handler.stream.flush()
    assert handler.shouldRollover(record) == 1
    handler.close()


def test_size_and_time_rotating_handler_rolls_on_time(tmp_path, monkeypatch):
    monkeypatch.setattr(TimedRotatingFileHandler, "shouldRollover", lambda self, record: 1)

    handler = core_logging.SizeAndTimeRotatingHandler(
        filename=str(tmp_path / "x.log"),
        when="midnight",
        interval=1,
        backupCount=1,
        encoding="utf-8",
        max_bytes=10_000,
    )
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="x",
        args=(),
        exc_info=None,
    )
    assert handler.shouldRollover(record) == 1
    handler.close()


def test_init_logging_sets_root_handlers(tmp_path, monkeypatch):
    class _Cfg:
        dir = str(tmp_path)
        level = "INFO"
        max_bytes = "10KB"
        backup_count = 2

    monkeypatch.setattr(core_logging, "logging_config", _Cfg)

    core_logging.init_logging()

    root = logging.getLogger()
    assert len(root.handlers) >= 1
    assert any(isinstance(h, core_logging.SizeAndTimeRotatingHandler) for h in root.handlers)
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)
