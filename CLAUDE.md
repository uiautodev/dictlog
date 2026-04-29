# dictlog

轻量级结构化日志库，受 structlog 启发，提供彩色终端输出和上下文绑定。

## 非常重要的注意事项

- 如果涉及到使用相关的代码更新，需要同步更新README
- 如果README.md变动了，README_EN.md也需要同步更新。要以README.md为主

## 开发

- 包管理: uv
- Python: >=3.9
- 测试: pytest (`uv run pytest -v`)
- Lint/Format: ruff (`uv run ruff check .` / `uv run ruff format .`)
- Pre-commit: `uv run pre-commit run --all-files`

## 项目结构

- `dictlog.py` — 核心库，包含 `StructLog`、`ColorFormatter`、`get_logger`
- `test_dictlog.py` — pytest 测试
- `.pre-commit-config.yaml` — pre-commit hooks (ruff, detect-secrets 等)

## 注意事项

- 使用 `from __future__ import annotations` 兼容低版本 Python 的类型注解语法
- 日志格式带 ANSI 颜色码，测试中检查内容时注意颜色转义字符的影响
- detect-secrets baseline 文件 (`.secrets.baseline`) 需要提交到仓库

## 发布到 PyPI

CI 使用 GitHub Actions + PyPI Trusted Publishers（OIDC），无需手动管理 token。

**首次配置：**
1. GitHub repo Settings → Environments → 新建 `pypi` 环境
2. PyPI 项目页面 → Publishing → Add a new publisher：
   - Owner: `uiautodev`
   - Repository: `dictlog`
   - Workflow: `publish.yml`
   - Environment: `pypi`

**发布流程：**
1. 修改 pyproject.toml 中的 `version`
2. 推送代码，创建 GitHub Release
3. Actions 自动构建并发布到 PyPI
