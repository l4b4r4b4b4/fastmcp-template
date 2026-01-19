{%- set use_demo_tools = (cookiecutter.template_variant == 'full') or (cookiecutter.template_variant == 'custom' and cookiecutter.include_demo_tools == 'yes') -%}
{%- set use_secret_tools = (cookiecutter.template_variant == 'full') or (cookiecutter.template_variant == 'custom' and cookiecutter.include_secret_tools == 'yes') -%}
{%- set use_langfuse = (cookiecutter.template_variant in ['standard', 'full']) or (cookiecutter.template_variant == 'custom' and cookiecutter.include_langfuse == 'yes') -%}
# {{ cookiecutter.project_name }}

[![CI](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/{{ cookiecutter.project_slug }}.svg)](https://pypi.org/project/{{ cookiecutter.project_slug }}/)
[![Python {{ cookiecutter.python_version }}+](https://img.shields.io/badge/python-{{ cookiecutter.python_version }}%2B-blue.svg)](https://www.python.org/downloads/)
{% if cookiecutter.license == "MIT" %}[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT){% endif %}
{% if cookiecutter.license == "Apache-2.0" %}[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0){% endif %}
{% if cookiecutter.license == "GPL-3.0" %}[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0){% endif %}
{% if cookiecutter.license == "BSD-3-Clause" %}[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause){% endif %}
{% if cookiecutter.license == "Proprietary" %}[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE){% endif %}
[![GHCR](https://img.shields.io/badge/GHCR-{{ cookiecutter.project_slug }}-blue?logo=github)](https://ghcr.io/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }})

{{ cookiecutter.project_description }}

Built with [FastMCP](https://github.com/jlowin/fastmcp) and [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache) for efficient handling of large data in AI agent tools.

## Features

- ✅ **Reference-Based Caching** - Return references instead of large data, reducing context window usage
- ✅ **Preview Generation** - Automatic previews for large results (sample, truncate, paginate strategies)
- ✅ **Pagination** - Navigate large datasets without loading everything at once
- ✅ **Access Control** - Separate user and agent permissions for sensitive data
- ✅ **Private Computation** - Let agents compute with values they cannot see
- ✅ **Docker Ready** - Production-ready containers with Python slim base image
- ✅ **GitHub Actions** - CI/CD with PyPI publishing and GHCR containers
{% if use_langfuse %}
- ✅ **Langfuse Tracing** - Built-in observability integration
{% endif %}
- ✅ **Type-Safe** - Full type hints with Pydantic models
- ✅ **Testing Ready** - pytest with 73% coverage requirement
- ✅ **Pre-commit Hooks** - Ruff formatting and linting

## Quick Start

### Prerequisites

- Python {{ cookiecutter.python_version }}+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}
cd {{ cookiecutter.project_slug }}

# Install dependencies
uv sync

# Run the server (stdio mode for Claude Desktop)
uv run {{ cookiecutter.project_slug }}

# Run the server (SSE/HTTP mode for deployment)
uv run {{ cookiecutter.project_slug }} --transport sse --port 8000
```

### Install from PyPI

```bash
# Run directly with uvx (no install needed)
uvx {{ cookiecutter.project_slug }} stdio

# Or install globally
uv tool install {{ cookiecutter.project_slug }}
{{ cookiecutter.project_slug }} --help
```

### Docker Deployment

```bash
# Pull and run from GHCR
docker pull ghcr.io/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}:latest
docker run -p 8000:8000 ghcr.io/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}:latest

# Or build locally with Docker Compose
docker compose up

# Build images manually
docker compose --profile build build base
docker compose build
```

### Using with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "{{ cookiecutter.project_slug }}": {
      "command": "uv",
      "args": ["run", "{{ cookiecutter.project_slug }}"],
      "cwd": "/path/to/{{ cookiecutter.project_slug }}"
    }
  }
}
```

### Using with Zed

The project includes `.zed/settings.json` pre-configured for MCP context servers.

{% if use_demo_tools %}
## Example Tools

The project includes several example tools demonstrating different patterns:

### Simple Tool (No Caching)

```python
@mcp.tool
def hello(name: str = "World") -> dict[str, Any]:
    """Say hello to someone."""
    return {"message": f"Hello, {name}!"}
```

### Cached Tool (Public Namespace)

```python
@mcp.tool
@cache.cached(namespace="public")
async def generate_items(count: int = 10, prefix: str = "item") -> list[dict]:
    """Generate items with automatic caching for large results."""
    return [{"id": i, "name": f"{prefix}_{i}"} for i in range(count)]
```

### Private Computation (EXECUTE Permission)

```python
@mcp.tool
def store_secret(name: str, value: float) -> dict[str, Any]:
    """Store a secret that agents can use but not read."""
    secret_policy = AccessPolicy(
        user_permissions=Permission.FULL,
        agent_permissions=Permission.EXECUTE,  # Can use, cannot see
    )
    ref = cache.set(key=f"secret_{name}", value=value, policy=secret_policy)
    return {"ref_id": ref.ref_id}

@mcp.tool
def compute_with_secret(secret_ref: str, multiplier: float = 1.0) -> dict[str, Any]:
    """Compute using a secret without revealing it."""
    secret = cache.resolve(secret_ref, actor=DefaultActor.system())
    return {"result": secret * multiplier}
```

{% endif %}
## Project Structure

```
{{ cookiecutter.project_slug }}/
├── app/                     # Application code
│   ├── __init__.py          # Version export
│   ├── server.py            # Main server with tools
│   ├── tools/               # Tool modules
│   └── __main__.py          # CLI entry point
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures
│   └── test_server.py       # Server tests
├── docker/
│   ├── Dockerfile.base      # Python slim base image with dependencies
│   ├── Dockerfile           # Production image (extends base)
│   └── Dockerfile.dev       # Development with hot reload
├── .github/
│   └── workflows/
│       ├── ci.yml           # CI pipeline (lint, test, security)
│       ├── publish.yml      # PyPI trusted publisher
│       └── release.yml      # Docker build & publish to GHCR
├── .agent/                  # AI assistant workspace
│   └── goals/
│       └── 00-Template-Goal/  # Goal tracking template
├── pyproject.toml           # Project config
├── docker-compose.yml       # Local development & production
├── flake.nix                # Nix dev shell
└── .rules                   # AI assistant guidelines
```

## Development

### Setup

```bash
# Install dependencies
uv sync

# Install pre-commit and pre-push hooks
uv run pre-commit install --install-hooks
uv run pre-commit install --hook-type pre-push
```

### Running Tests

```bash
uv run pytest
uv run pytest --cov  # With coverage
```

### Linting and Formatting

```bash
uv run ruff check . --fix
uv run ruff format .
```

### Type Checking

```bash
uv run mypy app/
```

### Docker Development

```bash
# Run development container with hot reload
docker compose --profile dev up

# Build base image (for publishing)
docker compose --profile build build base

# Build all images
docker compose build
```

### Using Nix (Optional)

```bash
nix develop  # Enter dev shell with all tools
```

## Configuration
{% if use_langfuse %}

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | - |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | - |
| `LANGFUSE_HOST` | Langfuse host URL | `https://cloud.langfuse.com` |
{% endif %}

### CLI Commands

```bash
uvx {{ cookiecutter.project_slug }} --help

Commands:
  stdio             Start server in stdio mode (for Claude Desktop and local CLI)
  sse               Start server in SSE mode (Server-Sent Events)
  streamable-http   Start server in streamable HTTP mode (recommended for remote/Docker)

# Examples:
uvx {{ cookiecutter.project_slug }} stdio                          # Local CLI mode
uvx {{ cookiecutter.project_slug }} sse --port 8000                # SSE on port 8000
uvx {{ cookiecutter.project_slug }} streamable-http --host 0.0.0.0 # Docker/remote mode
```

## CI/CD Workflow

This project uses a CI-gated workflow to ensure code quality and safe releases:

```
┌─────────────────────────────────────────────────────────────┐
│  Feature Branch → Open PR                                   │
│         ↓                                                    │
│  CI Runs (lint, test, security)                            │
│         ↓                                                    │
│  ✅ CI Must Pass (enforced by branch protection)           │
│         ↓                                                    │
│  Merge to main                                              │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  CI Re-runs on main                                         │
│         ↓                                                    │
│  Release Workflow waits for CI Success                      │
│         ↓                                                    │
│  Docker Images Built & Pushed to GHCR                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Manually Create GitHub Release                             │
│         ↓                                                    │
│  Publish Workflow verifies Release succeeded                │
│         ↓                                                    │
│  Package Published to PyPI                                  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  CD Workflow deploys (staging/production)                   │
└─────────────────────────────────────────────────────────────┘
```

**Key Safeguards:**
- ✅ Branch protection ensures CI passes before merge
- ✅ Tag pushes verify CI passed before building images
- ✅ Publish workflow verifies Release succeeded before PyPI upload
- ✅ CD workflow only deploys after Release completes

**Manual Gates:**
- 🔒 Creating GitHub Release (allows review before PyPI publish)
- 🔒 Production deployments (requires manual approval)

## Publishing

### PyPI

Configure trusted publisher at [PyPI](https://pypi.org/manage/account/publishing/):
- Project name: `{{ cookiecutter.project_slug }}`
- Owner: `{{ cookiecutter.github_username }}`
- Repository: `{{ cookiecutter.project_slug }}`
- Workflow: `publish.yml`
- Environment: `pypi`

### Docker Images

Images are automatically published to GHCR on:
- Push to `main` branch → `latest` tag
- Version tags (`v*.*.*`) → `latest`, `v0.0.1`, `0.0.1`, `0.0` tags

## License

{{ cookiecutter.license }} License - see [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Related Projects

- [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache) - Reference-based caching for MCP servers
- [FastMCP](https://github.com/jlowin/fastmcp) - High-performance MCP server framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - The underlying protocol specification
