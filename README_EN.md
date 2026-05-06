# dictlog

[中文文档](README.md)

A lightweight structured logging library inspired by [structlog](https://github.com/hynek/structlog), featuring colored terminal output and context binding.

Compared to structlog, dictlog's method signatures are fully type-annotated, enabling proper editor autocomplete and hints.

While not as feature-rich as structlog, you won't have to deal with editor errors anymore.

Built on top of Python's standard `logging` library for full compatibility.

![Demo](docs/demo.png)

## Features

- Structured logging with key-value context binding (`bind`/`unbind`)
- Colored terminal output with compact format
- Supports 6 log levels: `TRACE` < `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`
- Supports child loggers (names separated by `.`)
- `exception()` method automatically attaches exception stack traces; all log methods support `exc_info`, `*args` (`%`-style formatting), and `stacklevel` parameters, consistent with the standard `logging` library
- Works out of the box, zero configuration required
- Complete type annotations, editor-friendly

## Installation

```bash
pip install dictlog
# or using uv
uv add dictlog
```

Requires Python >= 3.9.

## Usage

```python
import dictlog

# Basic usage
log = dictlog.get_logger("myapp")
# Adjust log level, equivalent to logging.DEBUG, default is WARNING
log.level = dictlog.DEBUG

# Supported log levels: TRACE(5) < DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40) < CRITICAL(50)
log.trace("detailed debug info", user_id=123)  # Most verbose debugging
log.debug("debug message", port=8080)
log.info("server started", port=8080)

# %-style format args, consistent with logging usage
log.info("hello %s", "world")
log.debug("x=%d y=%d", 1, 2)

# Custom stacklevel (default 1, meaning the direct caller's frame)
def my_wrapper():
    log.info("from wrapper", stacklevel=2)  # reports the line that called my_wrapper()

# Bind context, automatically included in subsequent calls
log = log.bind(user="alice")
log.info("user logged in")          # includes user=alice
log = log.unbind("user")
log.info("context removed")         # no longer includes user

# Capture exception with stack trace, consistent with logging usage
try:
    1 / 0
except ZeroDivisionError:
    log.error("something went wrong", exc_info=True)
    # or use exception(), which defaults to exc_info=True
    log.exception("something went wrong")
```

## How dictlog calls logging

```python
log = dictlog.get_logger("foo", name=123)
log.info("hello")
```

is equivalent to

```python
root_log = logging.getLogger("dictlog")
if not root_log.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(_formatter)  # ColorFormatter
    root_log.addHandler(handler)
log = logging.getLogger("dictlog.foo")
log.info("hello %s", "name=123")
```

> If you don't want the `dictlog.` prefix, you can modify `dictlog._ROOT_NAME`


## Development

```bash
# Install dependencies
uv sync

# Run pre-commit hooks
uv run pre-commit run --all-files

# Run example
uv run dictlog.py
```

## License

[MIT](LICENSE)
