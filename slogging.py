from __future__ import annotations

import logging
import datetime
from typing import Any

from colored import Fore, Style

TRACE = 5
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

logging.addLevelName(TRACE, "TRACE")


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        TRACE: Fore.DARK_GRAY,
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, "")
        level = f"{record.levelname[:1]}"
        msg = f"{record.getMessage()}"
        dt = datetime.datetime.fromtimestamp(record.created)
        time_str = dt.strftime("%y%m%d %H:%M:%S")
        loc = f"{record.filename}:{record.lineno}"
        name = record.name.split('.', maxsplit=1)[-1]
        line = f"{color}[{level}:{name} {time_str} {loc}]{Style.RESET} {msg}"
        if record.exc_info and record.exc_info[0] is not None:
            line += f"\n{self.formatException(record.exc_info)}"
        return line


_ROOT_NAME = "slogging"
_formatter: ColorFormatter | None = None


def _ensure_root():
    global _formatter
    root = logging.getLogger(_ROOT_NAME)
    if not root.handlers:
        _formatter = ColorFormatter()
        handler = logging.StreamHandler()
        handler.setFormatter(_formatter)
        root.addHandler(handler)
    return root


class StructLog:
    def __init__(
        self,
        name=None,
        _context=None,
        level=logging.NOTSET,
    ):
        _ensure_root()
        full_name = f"{_ROOT_NAME}.{name}" if name else _ROOT_NAME
        self._logger = logging.getLogger(full_name)
        self._context = _context or {}
        if level != logging.NOTSET:
            self._logger.setLevel(level)

    @property
    def level(self) -> int:
        return self._logger.getEffectiveLevel()

    @level.setter
    def level(self, value: int) -> None:
        self._logger.setLevel(value)

    def bind(self, **kwargs) -> "StructLog":
        new = StructLog.__new__(StructLog)
        new._logger = self._logger
        new._context = {**self._context, **kwargs}
        return new

    def unbind(self, *keys) -> "StructLog":
        new = StructLog.__new__(StructLog)
        new._logger = self._logger
        new._context = {k: v for k, v in self._context.items() if k not in keys}
        return new

    def trace(self, event: str, **kwargs: Any):
        self._logger.log(TRACE, self._fmt(event, **kwargs), stacklevel=2)

    def _fmt(self, event: str, **kwargs: Any) -> str:
        parts = {**self._context, **kwargs}
        if parts:
            ctx = " ".join(
                f"{Fore.LIGHT_GREEN_3}{k}{Style.RESET}={Fore.LIGHT_PINK_3}{v}{Style.RESET}"
                for k, v in parts.items()
            )
            return f"{event} {ctx}"
        return event

    def debug(self, event: str, **kwargs: Any):
        self._logger.debug(self._fmt(event, **kwargs), stacklevel=2)

    def info(self, event: str, **kwargs: Any):
        self._logger.info(self._fmt(event, **kwargs), stacklevel=2)

    def warning(self, event: str, **kwargs: Any):
        self._logger.warning(self._fmt(event, **kwargs), stacklevel=2)

    def error(self, event: str, **kwargs: Any):
        self._logger.error(self._fmt(event, **kwargs), stacklevel=2)

    def exception(self, event: str, **kwargs: Any):
        self._logger.exception(self._fmt(event, **kwargs), stacklevel=2)

    def critical(self, event: str, **kwargs: Any):
        self._logger.critical(self._fmt(event, **kwargs), stacklevel=2)


def get_logger(_name=None, **kwargs):
    slog = StructLog(_name)
    if kwargs:
        slog = slog.bind(**kwargs)
    return slog


if __name__ == "__main__":
    slog = get_logger()
    slog.level = TRACE
    slog.trace("trace message", user="alice", action="login")
    slog.debug("debug message", user="bob", action="logout")
    slog.info("info message", user="charlie", action="update")
    slog.warning("warning message", user="dave", action="delete")
    slog.error("error message", user="eve", action="create")
