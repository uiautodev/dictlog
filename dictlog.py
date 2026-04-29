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
        level = record.levelname[:1]
        msg = record.getMessage()
        dt = datetime.datetime.fromtimestamp(record.created)
        time_str = dt.strftime("%y%m%d %H:%M:%S")
        loc = f"{record.filename}:{record.lineno}"
        name = record.name.split('.', maxsplit=1)[-1]
        line = f"{color}[{level}:{name} {time_str} {loc}]{Style.RESET} {msg}"
        if record.exc_info and record.exc_info[0] is not None:
            line += f"\n{self.formatException(record.exc_info)}"
        return line


_ROOT_NAME = "dictlog"
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

    def trace(self, message: str, /, **kwargs: Any):
        self._logger.log(TRACE, self._fmt(message, **kwargs), stacklevel=2)

    def _fmt(self, message: str, /, **kwargs: Any) -> str:
        parts = {**self._context, **kwargs}
        if parts:
            ctx = " ".join(
                f"{Fore.LIGHT_GREEN_3}{k}{Style.RESET}={Fore.LIGHT_PINK_3}{v}{Style.RESET}"
                for k, v in parts.items()
            )
            return f"{message} {ctx}"
        return message

    def debug(self, message: str, /, **kwargs: Any):
        self._logger.debug(self._fmt(message, **kwargs), stacklevel=2)

    def info(self, message: str, /, **kwargs: Any):
        self._logger.info(self._fmt(message, **kwargs), stacklevel=2)

    def warning(self, message: str, /, **kwargs: Any):
        self._logger.warning(self._fmt(message, **kwargs), stacklevel=2)

    def error(self, message: str, /, **kwargs: Any):
        self._logger.error(self._fmt(message, **kwargs), stacklevel=2)

    def exception(self, message: str, /, **kwargs: Any):
        self._logger.exception(self._fmt(message, **kwargs), stacklevel=2)

    def critical(self, message: str, /, **kwargs: Any):
        self._logger.critical(self._fmt(message, **kwargs), stacklevel=2)


def get_logger(name=None, /, level=logging.NOTSET, **kwargs):
    log = StructLog(name, level=level)
    if kwargs:
        log = log.bind(**kwargs)
    return log


if __name__ == "__main__":
    log = get_logger()
    log.level = TRACE
    log.trace("trace message", user="alice", action="login")
    log.debug("debug message", user="bob", action="logout")
    log.info("info message", user="charlie", action="update")
    log.warning("warning message", user="dave", action="delete")
    log.error("error message", user="eve", action="create")
