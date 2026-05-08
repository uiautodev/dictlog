from __future__ import annotations

import logging
import sys
import datetime
from typing import Any, Union

from colored import Fore, Style

TRACE = 5
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

logging.addLevelName(TRACE, "TRACE")

ExcInfoType = Union[
    bool,
    BaseException,
    tuple[type[BaseException], BaseException, Any],
    tuple[None, None, None],
    None,
]


def _should_enable_color() -> bool:
    try:
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    except (AttributeError, OSError):
        return False


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        TRACE: Fore.DARK_GRAY,
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color_enabled = _should_enable_color()

    def format(self, record: logging.LogRecord) -> str:
        # 使用 extra 中的 dictlog_msg（带颜色的格式化消息），如果存在
        # 否则回退到标准 msg（纯文本，兼容 basicConfig）
        msg = getattr(record, "dictlog_msg", None)
        if msg is None:
            msg = record.getMessage()

        color = self.LEVEL_COLORS.get(record.levelno, "") if self._color_enabled else ""
        reset = Style.RESET if self._color_enabled else ""
        level = record.levelname[:1]
        dt = datetime.datetime.fromtimestamp(record.created)
        time_str = dt.strftime("%y%m%d %H:%M:%S")
        loc = f"{record.filename}:{record.lineno}"
        name = record.name.split('.', maxsplit=1)[-1]
        line = f"{color}[{level}:{name} {time_str} {loc}]{reset} {msg}"
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
        self._color_enabled = _should_enable_color()
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
        new._color_enabled = self._color_enabled
        return new

    def unbind(self, *keys) -> "StructLog":
        new = StructLog.__new__(StructLog)
        new._logger = self._logger
        new._context = {k: v for k, v in self._context.items() if k not in keys}
        new._color_enabled = self._color_enabled
        return new

    def trace(
        self,
        message: str,
        /,
        *args: Any,
        exc_info: ExcInfoType = False,
        stacklevel: int = 1,
        **kwargs: Any,
    ):
        msg, extra = self._fmt(message, *args, **kwargs)
        self._logger.log(
            TRACE, msg, stacklevel=stacklevel + 1, exc_info=exc_info, extra=extra
        )

    def _fmt(self, message: str, /, *args: Any, **kwargs: Any) -> tuple[str, dict[str, Any]]:
        """格式化消息，返回 (纯文本消息, extra 字典)

        纯文本消息用于兼容 basicConfig，extra 中包含带颜色的格式化消息
        """
        if args:
            message = message % args
        parts = {**self._context, **kwargs}
        extra = {}
        if parts:
            # 纯文本版本的上下文
            plain_ctx = " ".join(f"{k}={v}" for k, v in parts.items())
            plain_msg = f"{message} {plain_ctx}"

            # 带颜色的格式化消息放在 dictlog_msg 中
            if self._color_enabled:
                color_ctx = " ".join(
                    f"{Fore.LIGHT_GREEN_3}{k}{Style.RESET}={Fore.LIGHT_PINK_3}{v}{Style.RESET}"
                    for k, v in parts.items()
                )
                extra["dictlog_msg"] = f"{message} {color_ctx}"
            else:
                extra["dictlog_msg"] = plain_msg

            return plain_msg, extra
        return message, extra

    def debug(
        self,
        message: str,
        /,
        *args: Any,
        exc_info: ExcInfoType = False,
        stacklevel: int = 1,
        **kwargs: Any,
    ):
        msg, extra = self._fmt(message, *args, **kwargs)
        self._logger.debug(
            msg, stacklevel=stacklevel + 1, exc_info=exc_info, extra=extra
        )

    def info(
        self,
        message: str,
        /,
        *args: Any,
        exc_info: ExcInfoType = False,
        stacklevel: int = 1,
        **kwargs: Any,
    ):
        msg, extra = self._fmt(message, *args, **kwargs)
        self._logger.info(
            msg, stacklevel=stacklevel + 1, exc_info=exc_info, extra=extra
        )

    def warning(
        self,
        message: str,
        /,
        *args: Any,
        exc_info: ExcInfoType = False,
        stacklevel: int = 1,
        **kwargs: Any,
    ):
        msg, extra = self._fmt(message, *args, **kwargs)
        self._logger.warning(
            msg, stacklevel=stacklevel + 1, exc_info=exc_info, extra=extra
        )

    def error(
        self,
        message: str,
        /,
        *args: Any,
        exc_info: ExcInfoType = False,
        stacklevel: int = 1,
        **kwargs: Any,
    ):
        msg, extra = self._fmt(message, *args, **kwargs)
        self._logger.error(
            msg, stacklevel=stacklevel + 1, exc_info=exc_info, extra=extra
        )

    def exception(
        self,
        message: str,
        /,
        *args: Any,
        exc_info: ExcInfoType = True,
        stacklevel: int = 1,
        **kwargs: Any,
    ):
        msg, extra = self._fmt(message, *args, **kwargs)
        self._logger.exception(
            msg, stacklevel=stacklevel + 1, exc_info=exc_info, extra=extra
        )

    def critical(
        self,
        message: str,
        /,
        *args: Any,
        exc_info: ExcInfoType = False,
        stacklevel: int = 1,
        **kwargs: Any,
    ):
        msg, extra = self._fmt(message, *args, **kwargs)
        self._logger.critical(
            msg, stacklevel=stacklevel + 1, exc_info=exc_info, extra=extra
        )


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
