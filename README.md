# slogging

受 [structlog](https://github.com/hynek/structlog) 启发的轻量级结构化日志库，提供彩色终端输出和上下文绑定。

相比 structlog，slogging 的方法签名完全标注了类型，编辑器可以正常补全和提示。

功能肯定没有 structlog 强大，但是终于不用再看编辑器的错误提示了。

由于是基于系统库 logging 实现，使用上完全兼容。

## 特性

- 结构化日志 + key-value 上下文绑定（`bind`/`unbind`）
- 彩色终端输出，紧凑格式
- 支持子 logger（用 `.` 分隔名称）
- `exception()` 方法自动附加异常堆栈
- 开箱即用，零配置
- 完整的类型标注，编辑器友好

## 安装

slogging 在 PyPI 上已经有别人申请了，但是我也没想到更好的名字，所以就先通过 git 安装吧。

```bash
pip install git+https://github.com/uiautodev/slogging.git@x.x.x
# 或使用 uv
uv add git+https://github.com/uiautodev/slogging.git@x.x.x
```

要求 Python >= 3.9。

## 使用

```python
import slogging

# 基本用法
slog = slogging.get_logger("myapp")
# 调整日志级别，与 logging.DEBUG 等价，默认是 WARNING
slog.level = slogging.DEBUG

slog.info("server started", port=8080)

# 绑定上下文，后续调用自动携带
slog = slog.bind(user="alice")
slog.info("user logged in")          # 自带 user=alice
slog = slog.unbind("user")
slog.info("context removed")         # 不再包含 user
```

## slogging 是如何调用 logging 的

```python
slog = slogging.get_logger("foo", name=123)
slog.info("hello")
```

等价于

```python
root_slog = logging.getLogger("slogging")
if not root_slog.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(_formatter)  # ColorFormatter
    root_slog.addHandler(handler)
slog = logging.getLogger("slogging.foo")
slog.info("hello %s", "name=123")
```

> 如果不想使用 `slogging.` 开头，可以通过修改 `slogging._ROOT_NAME` 实现


## 开发

```bash
# 安装依赖
uv sync

# 运行 pre-commit hooks
uv run pre-commit run --all-files

# 运行示例
uv run slogging.py
```

## License

MIT
