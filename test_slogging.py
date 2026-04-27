import logging
import pytest

from slogging import (
    StructLog,
    get_logger,
    ColorFormatter,
    DEBUG,
    INFO,
    WARNING,
    ERROR,
)


class TestGetLogger:
    def test_default_name(self):
        log = get_logger()
        assert isinstance(log, StructLog)

    def test_with_name(self):
        log = get_logger("myapp")
        assert isinstance(log, StructLog)

    def test_with_kwargs_binds_context(self):
        log = get_logger("ctx", port=8080)
        assert log._context == {"port": 8080}

    def test_with_level(self):
        log = get_logger("lv", level=WARNING)
        assert log.level == WARNING


class TestBindUnbind:
    def test_bind_returns_new_instance(self):
        log = get_logger("b1")
        log2 = log.bind(user="alice")
        assert log2 is not log
        assert log._context == {}
        assert log2._context == {"user": "alice"}

    def test_bind_merges_context(self):
        log = get_logger("b2").bind(a=1)
        log2 = log.bind(b=2)
        assert log2._context == {"a": 1, "b": 2}

    def test_unbind_returns_new_instance(self):
        log = get_logger("u1").bind(a=1, b=2)
        log2 = log.unbind("a")
        assert log2 is not log
        assert log._context == {"a": 1, "b": 2}
        assert log2._context == {"b": 2}

    def test_unbind_multiple_keys(self):
        log = get_logger("u2").bind(a=1, b=2, c=3)
        log2 = log.unbind("a", "c")
        assert log2._context == {"b": 2}


class TestLevel:
    def test_default_level(self):
        log = get_logger("lv1")
        assert log.level == logging.WARNING

    def test_set_level(self):
        log = get_logger("lv2")
        log.level = DEBUG
        assert log.level == DEBUG


class TestFormatting:
    def test_fmt_with_context(self):
        log = get_logger("f1").bind(k="v")
        result = log._fmt("hello")
        assert "hello" in result
        assert "k" in result
        assert "v" in result

    def test_fmt_without_context(self):
        log = get_logger("f2")
        assert log._fmt("hello") == "hello"

    def test_fmt_context_overrides(self):
        log = get_logger("f3").bind(a=1)
        result = log._fmt("msg", a=2)
        # context value overridden: a=2 should appear (with possible ANSI codes)
        assert "a" in result and "2" in result


class TestColorFormatter:
    def test_format_returns_string(self):
        fmt = ColorFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=1,
            msg="hello", args=(), exc_info=None,
        )
        result = fmt.format(record)
        assert isinstance(result, str)
        assert "hello" in result

    def test_format_includes_level(self):
        fmt = ColorFormatter()
        record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="", lineno=1,
            msg="warn msg", args=(), exc_info=None,
        )
        result = fmt.format(record)
        assert "W" in result  # levelname[:1]

    def test_format_with_exception(self):
        fmt = ColorFormatter()
        try:
            raise ValueError("oops")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=1,
            msg="err", args=(), exc_info=exc_info,
        )
        result = fmt.format(record)
        assert "ValueError" in result
        assert "oops" in result


class TestLogLevels:
    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def test_debug(self):
        log = get_logger("d", level=DEBUG)
        with self.caplog.at_level(DEBUG, logger="_sroot.d"):
            log.debug("dbg", x=1)
        assert any("dbg" in r.message for r in self.caplog.records)

    def test_info(self):
        log = get_logger("i")
        with self.caplog.at_level(INFO, logger="_sroot.i"):
            log.info("inf", y=2)
        assert any("inf" in r.message for r in self.caplog.records)

    def test_warning(self):
        log = get_logger("w")
        with self.caplog.at_level(WARNING, logger="_sroot.w"):
            log.warning("wrn")
        assert any("wrn" in r.message for r in self.caplog.records)

    def test_error(self):
        log = get_logger("e")
        with self.caplog.at_level(ERROR, logger="_sroot.e"):
            log.error("err", detail="x")
        assert any("err" in r.message for r in self.caplog.records)

    def test_exception(self):
        log = get_logger("exc")
        with self.caplog.at_level(ERROR, logger="_sroot.exc"):
            try:
                1 / 0
            except ZeroDivisionError:
                log.exception("crash")
        records = [r for r in self.caplog.records if "crash" in r.message]
        assert len(records) == 1
        assert records[0].exc_info is not None
