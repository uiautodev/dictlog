# slogging

受 [structlog](https://github.com/hynek/structlog) 启发的轻量级结构化日志库，提供彩色终端输出和上下文绑定。

相比 structlog，slogging 的方法签名完全标注了类型，编辑器可以正常补全和提示。

## 特性

- 结构化日志 + key-value 上下文绑定（`bind`/`unbind`）
- 彩色终端输出，紧凑格式
- 支持子 logger（用 `.` 分隔名称）
- 开箱即用，零配置
- 完整的类型标注，编辑器友好

## 安装

```bash
pip install git+https://github.com/uiautodev/slogging.git
# 或使用 uv
uv add git+https://github.com/uiautodev/slogging.git
```

要求 Python >= 3.9。

## 使用

```python
from slogging import get_logger, DEBUG

# 基本用法
log = get_logger("myapp")
log.info("server started", port=8080)

# 绑定上下文，后续调用自动携带
log = log.bind(user="alice")
log.info("user logged in")          # 自带 user=alice
log = log.unbind("user")
log.info("context removed")         # 不再包含 user

# 调整日志级别，默认跟随logging
log.level = DEBUG
log.debug("detailed info")
```

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
