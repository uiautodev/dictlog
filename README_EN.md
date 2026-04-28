# slogging

[中文文档](README.md)

A lightweight structured logging library inspired by [structlog](https://github.com/hynek/structlog), featuring colored terminal output and context binding.

Compared to structlog, slogging's method signatures are fully type-annotated, enabling proper editor autocomplete and hints.

While not as feature-rich as structlog, you won't have to deal with editor errors anymore.

Built on top of Python's standard `logging` library for full compatibility.

## Features

- Structured logging with key-value context binding (`bind`/`unbind`)
- Colored terminal output with compact format
- Supports 6 log levels: `TRACE` < `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`
- Supports child loggers (names separated by `.`)
- `exception()` method automatically attaches exception stack traces
- Works out of the box, zero configuration required
- Complete type annotations, editor-friendly

## Installation

The name "slogging" is already taken on PyPI, but I couldn't think of a better name, so please install via git for now.

```bash
pip install git+https://github.com/uiautodev/slogging.git@x.x.x
# or using uv
uv add git+https://github.com/uiautodev/slogging.git@x.x.x
```

Requires Python >= 3.9.

## Usage

```python
import slogging

# Basic usage
slog = slogging.get_logger("myapp")
# Adjust log level, equivalent to logging.DEBUG, default is WARNING
slog.level = slogging.DEBUG

# Supported log levels: TRACE(5) < DEBUG(10) < INFO(20) < WARNING(30) < ERROR(40) < CRITICAL(50)
slog.trace("detailed debug info", user_id=123)  # Most verbose debugging
slog.debug("debug message", port=8080)
slog.info("server started", port=8080)

# Bind context, automatically included in subsequent calls
slog = slog.bind(user="alice")
slog.info("user logged in")          # includes user=alice
slog = slog.unbind("user")
slog.info("context removed")         # no longer includes user
```

## How slogging calls logging

```python
slog = slogging.get_logger("foo", name=123)
slog.info("hello")
```

is equivalent to

```python
root_slog = logging.getLogger("slogging")
if not root_slog.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(_formatter)  # ColorFormatter
    root_slog.addHandler(handler)
slog = logging.getLogger("slogging.foo")
slog.info("hello %s", "name=123")
```

> If you don't want the `slogging.` prefix, you can modify `slogging._ROOT_NAME`


## Development

```bash
# Install dependencies
uv sync

# Run pre-commit hooks
uv run pre-commit run --all-files

# Run example
uv run slogging.py
```

## License

MIT
