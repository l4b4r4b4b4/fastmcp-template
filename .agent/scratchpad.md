# FastMCP Template: Clean Architecture & Release Improvements

## Status: Phase 1-4 Complete ✅

**Session Started:** 2024-12-13
**Branch:** `feature/ci-improvements`

---

## Overview

Improving fastmcp-template to be a production-ready MCP server template with:
1. Clean architecture (domain-organized modules)
2. Multiple transport support (stdio, sse, streamable-http)
3. Backend flexibility (memory, SQLite, Redis)
4. Dual release workflows (PyPI for uvx, Docker for containers)

**Reference:** [excel-mcp-server](https://github.com/haris-musa/excel-mcp-server) - 3k stars, clean architecture

---

## Task Checklist

### Phase 1: PyPI Release Workflow ✅
- [x] Create `.github/workflows/publish.yml` for PyPI trusted publishing
- [x] Verify `pyproject.toml` has correct metadata for PyPI
- [x] Add `typer` dependency for CLI
- [x] Test local build with `uv run hatch build`

### Phase 2: Typer CLI ✅
- [x] Create `app/__main__.py` with typer subcommands
- [x] Subcommands: `stdio`, `sse`, `streamable-http`
- [x] Environment variables: `FASTMCP_PORT`, `FASTMCP_HOST`
- [x] Update `pyproject.toml` scripts entry

### Phase 3: Configuration Module ✅
- [x] Create `app/config.py` with pydantic-settings
- [x] Backend selection: `CACHE_BACKEND=memory|sqlite|redis`
- [x] Redis config: `REDIS_URL`
- [x] SQLite config: `SQLITE_PATH` (XDG default)
- [x] Langfuse config in Settings class

### Phase 4: Refactor Tools into Modules ✅
- [x] Create `app/tools/demo.py` - hello, generate_items
- [x] Create `app/tools/cache.py` - get_cached_result
- [x] Create `app/tools/secrets.py` - store_secret, compute_with_secret
- [x] Create `app/tools/context.py` - test context tools
- [x] Create `app/tools/health.py` - health_check
- [x] Create `app/prompts/__init__.py` - template_guide, langfuse_guide
- [x] Simplify `app/server.py` from ~800 to ~180 lines
- [x] Update `app/__init__.py` exports
- [x] Update tests with new import paths
- [x] All 101 tests passing

### Phase 5: Documentation
- [ ] Create `TOOLS.md` documenting all available tools
- [ ] Update `README.md` with uvx usage examples
- [ ] Add transport/backend matrix to docs

### Phase 6: Testing & Verification
- [x] All existing tests pass (101/101)
- [ ] Test `uvx fastmcp-template stdio` locally (after PyPI publish)
- [ ] Test Docker build with new structure
- [ ] Verify PyPI publish workflow (dry run)

---

## Architecture

### Current Structure (Monolithic)
```
app/
├── __init__.py
├── server.py          # 800+ lines, everything in one file
├── tracing.py
└── tools/
    └── __init__.py    # Empty
```

### Target Structure (Domain-Organized)
```
app/
├── __init__.py
├── __main__.py          # typer CLI: stdio | sse | streamable-http
├── server.py            # FastMCP server factory (simplified)
├── config.py            # pydantic-settings for env config
├── tracing.py           # Langfuse integration (existing)
├── tools/
│   ├── __init__.py      # Tool registration
│   ├── demo.py          # hello, generate_items
│   ├── cache.py         # get_cached_result
│   ├── secrets.py       # store_secret, compute_with_secret
│   ├── admin.py         # admin_* tools
│   └── context.py       # enable_test_context, set_test_context, etc.
└── prompts/
    ├── __init__.py
    └── guides.py        # template_guide, langfuse_guide
```

---

## Transport & Backend Matrix

| Command | Transport | Default Backend | Use Case |
|---------|-----------|-----------------|----------|
| `uvx fastmcp-template stdio` | stdio | SQLite | Claude Desktop, local CLI |
| `uvx fastmcp-template sse` | SSE | Redis | HTTP deployment (deprecated) |
| `uvx fastmcp-template streamable-http` | streamable-http | Redis | **Recommended** for remote/Docker |

### Environment Variables

```bash
# Backend selection
CACHE_BACKEND=memory|sqlite|redis  # Default: auto (sqlite for stdio, redis for HTTP)

# Redis (for HTTP modes)
REDIS_URL=redis://localhost:6379

# SQLite (for stdio mode)
SQLITE_PATH=~/.local/share/fastmcp-template/cache.db

# Server (for HTTP modes)
FASTMCP_PORT=8000
FASTMCP_HOST=0.0.0.0

# Langfuse (optional)
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Release Workflows

### A. PyPI Release (NEW)

**Trigger:** GitHub Release published
**Purpose:** Enable `uvx fastmcp-template` usage

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/project/fastmcp-template
    permissions:
      id-token: write

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install build tools
        run: pip install hatch
      - name: Build package
        run: hatch build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

### B. Docker Release (Existing - Enhanced)

Already in `.github/workflows/release.yml`:
- Builds base + app images
- Multi-arch (amd64, arm64)
- Security scanning with Trivy
- Tags: `latest`, `v0.0.1`, `sha-abc1234`

**Enhancement:** Update Dockerfile CMD to use streamable-http as default.

---

## Implementation Notes

### Typer CLI Pattern (from excel-mcp-server)

```python
# app/__main__.py
import typer
from .server import run_stdio, run_sse, run_streamable_http

app = typer.Typer(help="FastMCP Template Server")

@app.command()
def stdio():
    """Start server in stdio mode (for Claude Desktop)"""
    run_stdio()

@app.command()
def sse():
    """Start server in SSE mode (deprecated, use streamable-http)"""
    run_sse()

@app.command()
def streamable_http():
    """Start server in streamable HTTP mode (recommended for remote)"""
    run_streamable_http()

if __name__ == "__main__":
    app()
```

### Config Pattern (pydantic-settings)

```python
# app/config.py
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    # Cache backend
    cache_backend: Literal["memory", "sqlite", "redis"] = "memory"
    redis_url: str = "redis://localhost:6379"
    sqlite_path: str = "~/.local/share/fastmcp-template/cache.db"

    # Server
    fastmcp_port: int = 8000
    fastmcp_host: str = "0.0.0.0"

    # Langfuse
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    model_config = {"env_prefix": "", "case_sensitive": False}

settings = Settings()
```

---

## Completed This Session

### ✅ Verified mcp-refcache v0.1.0 from PyPI
- Removed `[tool.uv.sources]` git override
- Fresh install: `rm -rf .venv uv.lock && uv sync`
- `uv pip show mcp-refcache` shows Version: 0.1.0
- All 101 tests passing

### ✅ Aligned Dependencies & Removed Pre-Push Hook
- Updated ruff in pre-commit to v0.14.9 (matches pyproject.toml >=0.14.8)
- Removed local pre-push pytest hook (rely on CI)
- Removed `.git/hooks/pre-push`
- Removed mypy from pre-commit (use Pyright via IDE)

### ✅ Typer CLI & PyPI Workflow
- Created `app/__main__.py` with typer CLI (stdio, sse, streamable-http)
- Created `.github/workflows/publish.yml` for PyPI trusted publishing
- Created `app/config.py` with pydantic-settings
- Updated dependencies to current versions:
  - fastmcp>=2.14.0, langfuse>=3.10.0, mcp-refcache>=0.1.0
  - Added pydantic-settings>=2.10.0
- Updated Docker to use `uv run fastmcp-template streamable-http`

### ✅ Modular Tools Architecture
- Created `app/tools/demo.py` - hello, generate_items
- Created `app/tools/context.py` - Langfuse test context tools
- Created `app/tools/secrets.py` - store_secret, compute_with_secret
- Created `app/tools/cache.py` - get_cached_result
- Created `app/tools/health.py` - health_check
- Created `app/prompts/__init__.py` - template_guide, langfuse_guide
- Simplified `app/server.py` from ~800 to ~180 lines
- Updated tests with new import paths
- All 101 tests passing

### Commits Made
```
1b50c7d chore: use mcp-refcache v0.1.0 from PyPI
187e9da chore: align ruff versions and remove pre-push hook
1a12506 feat: add typer CLI, PyPI publish workflow, and config module
e04a2bf refactor: modular tools architecture
```

---

## Future Improvements (Beyond This Session)

1. **Cookiecutter/Copier Template** - Generate new MCP projects from this template
2. **OpenTelemetry** - Optional OTLP export beyond Langfuse
3. **devcontainer.json** - GitHub Codespaces / VS Code support
4. **Health Endpoint** - `/health` for Kubernetes readiness probes
5. **Example Domain Tools** - Real-world example beyond demo tools
6. **Redis Cluster/Sentinel** - High availability Redis support

---

## Session Log

### 2024-12-13: Clean Architecture Implementation
- Verified mcp-refcache v0.1.0 from PyPI works
- Aligned ruff versions, removed pre-push hook, removed mypy from pre-commit
- Analyzed excel-mcp-server architecture for patterns
- Created comprehensive improvement plan
- **Phase 1 Complete:** PyPI publish workflow with trusted publisher
- **Phase 2 Complete:** Typer CLI with stdio/sse/streamable-http
- **Phase 3 Complete:** pydantic-settings config module
- **Phase 4 Complete:** Modular tools architecture
  - server.py reduced from 800+ to 180 lines
  - Tools organized into demo, context, secrets, cache, health modules
  - Prompts moved to dedicated module
- Updated Docker to use `uv run` and streamable-http default
- All 101 tests passing with updated imports

## Next Steps

### Immediate
- Create `TOOLS.md` documentation
- Update `README.md` with uvx usage examples
- Merge `feature/ci-improvements` to main

### After Merge
- Create GitHub Release to trigger PyPI publish
- Configure PyPI trusted publisher for fastmcp-template
- Test `uvx fastmcp-template stdio` after PyPI publish
- Test Docker image build
