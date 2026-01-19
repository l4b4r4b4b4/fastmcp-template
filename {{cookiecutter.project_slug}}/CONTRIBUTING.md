# Contributing to {{ cookiecutter.project_slug }}

Thank you for your interest in contributing to {{ cookiecutter.project_slug }}! This document outlines the conventions and guidelines for contributing to this project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) for dependency management
- [Nix](https://nixos.org/) (optional, for reproducible dev environment)

### Getting Started

```bash
# Clone the repository
git clone https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}
cd {{ cookiecutter.project_slug }}

# Option 1: Use Nix dev shell (recommended)
nix develop

# Option 2: Use uv directly
uv sync
```

## Code Conventions

### Type Annotations

**All functions and methods MUST have complete type annotations.**

```python
# ✅ Good
def resolve_reference(
    self,
    ref_id: str,
    namespace: str | None = None,
) -> CachedValue:
    ...

# ❌ Bad - missing return type
def resolve_reference(self, ref_id, namespace=None):
    ...
```

### MCP Cached Tool Return Types

**Tools decorated with `@cache.cached` MUST be annotated to return `dict[str, Any]`.**

The `@cache.cached` decorator wraps the raw return value in a structured cache response containing `ref_id`, `preview`, and metadata. The type annotation must match what the decorator actually returns, not the inner function's raw data.

```python
# ✅ Good - annotation matches decorator's wrapped response
@mcp.tool
@cache.cached(namespace="public")
async def generate_items(count: int = 10) -> dict[str, Any]:
    """Generate items with caching."""
    items = [{"id": i} for i in range(count)]
    return items  # Raw data, decorator wraps it

# ❌ Bad - annotation describes raw data, causes MCP schema mismatch
@mcp.tool
@cache.cached(namespace="public")
async def generate_items(count: int = 10) -> list[dict[str, Any]]:
    """This causes client validation errors."""
    return [{"id": i} for i in range(count)]
```

**Why this matters:** MCP generates tool schemas from Python type annotations. If a cached tool is annotated as returning `list[...]` but the decorator returns `dict[str, Any]`, clients receive a schema mismatch error.

### Pydantic Models for Inputs/Outputs

**All public API functions MUST use Pydantic models for complex inputs and outputs.**

```python
# ✅ Good - Pydantic model for structured input
class ResolveOptions(BaseModel):
    """Options for resolving a cache reference."""

    namespace: str | None = Field(
        default=None,
        description="Namespace to resolve from. If None, searches all accessible namespaces.",
    )
    permission: Permission = Field(
        default=Permission.READ,
        description="Required permission level for resolution.",
    )

def resolve(
    self,
    ref_id: str,
    options: ResolveOptions | None = None,
) -> CacheReference:
    ...

# ❌ Bad - unstructured dict input
def resolve(self, ref_id: str, **kwargs) -> dict:
    ...
```

### Docstrings

**All public functions, classes, and modules MUST have docstrings.**

We follow Google-style docstrings:

```python
def cache_value(
    self,
    key: str,
    value: Any,
    namespace: str = "public",
    policy: AccessPolicy | None = None,
) -> CacheReference:
    """Store a value in the cache and return a reference.

    This method stores the provided value in the specified namespace
    and returns a reference that can be used to retrieve it later.

    Args:
        key: Unique identifier for the cached value within the namespace.
        value: The value to cache. Must be JSON-serializable or a Pydantic model.
        namespace: Target namespace for storage. Defaults to "public".
        policy: Optional access policy. If None, uses namespace defaults.

    Returns:
        A CacheReference object containing the ref_id and metadata.

    Raises:
        PermissionError: If the caller lacks WRITE permission for the namespace.
        ValueError: If the key already exists and UPDATE permission is required.

    Example:
        ```python
        ref = cache.cache_value(
            key="user_data",
            value={"name": "Alice", "email": "alice@example.com"},
            namespace="user:123",
            policy=AccessPolicy(agent_permissions=Permission.EXECUTE),
        )
        print(ref.ref_id)  # "a1b2c3d4"
        ```
    """
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `CacheReference`, `AccessPolicy`)
- **Functions/Methods**: `snake_case` (e.g., `resolve_reference`, `get_cached_value`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `DEFAULT_TTL`, `MAX_PREVIEW_LENGTH`)
- **Private members**: Leading underscore (e.g., `_internal_cache`, `_validate_permissions`)

### File Organization

```
src/mcp_refcache/
├── __init__.py          # Public API exports
├── cache.py             # Core RefCache class
├── namespaces.py        # Namespace hierarchy
├── permissions.py       # Permission model and AccessPolicy
├── models.py            # Pydantic models (CacheReference, etc.)
├── backends/
│   ├── __init__.py
│   ├── memory.py        # In-memory backend
│   └── redis.py         # Redis backend
└── tools/
    ├── __init__.py
    └── mcp_tools.py     # FastMCP integration tools
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/mcp_refcache --cov-report=term

# Run specific test file
uv run pytest tests/test_cache.py

# Run with verbose output
uv run pytest -v
```

### Test Conventions

- Test files must be named `test_*.py`
- Test functions must be named `test_*`
- Use pytest fixtures for common setup
- Aim for ≥73% code coverage (threshold defined in `pyproject.toml`)
- Use `pytest-asyncio` for async tests

```python
import pytest
from mcp_refcache import RefCache, Permission

@pytest.fixture
def cache() -> RefCache:
    """Create a fresh cache instance for each test."""
    return RefCache(name="test-cache")

def test_cache_stores_value(cache: RefCache) -> None:
    """Test that values can be stored and retrieved."""
    ref = cache.set("key", {"data": "value"})

    assert ref.ref_id is not None
    assert cache.get(ref.ref_id) == {"data": "value"}

@pytest.mark.asyncio
async def test_async_resolution(cache: RefCache) -> None:
    """Test async reference resolution."""
    ref = await cache.async_set("key", "value")
    result = await cache.async_get(ref.ref_id)

    assert result == "value"
```

## Linting and Formatting

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
# Check for lint errors
uv run ruff check .

# Auto-fix lint errors
uv run ruff check . --fix

# Check formatting
uv run ruff format --check .

# Format code
uv run ruff format .
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code before committing:

```bash
uv run pre-commit install
```

## Git Workflow

### Branching

- `main` - stable, release-ready code
- `feature/*` - new features
- `fix/*` - bug fixes
- `refactor/*` - code improvements

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(namespaces): add hierarchical namespace support
fix(permissions): correct EXECUTE permission check
docs(readme): update installation instructions
test(cache): add tests for TTL expiration
refactor(backends): extract common backend interface
```

### Pull Requests

1. Create a feature branch from `main`
2. Make your changes with tests
3. Ensure all checks pass (`uv run ruff check . && uv run pytest`)
4. Open a PR with a clear description
5. Request review

## Architecture Guidelines

### Access Control

The permission system distinguishes between **users** (humans) and **agents** (AI):

```python
# User can see everything, agent can only use without seeing
policy = AccessPolicy(
    user_permissions=Permission.FULL,
    agent_permissions=Permission.EXECUTE,
)
```

### Namespace Hierarchy

Namespaces follow a hierarchical structure with permission inheritance:

```
public                    # Base namespace
├── session:abc123        # Session-scoped
├── user:456              # User-scoped
│   └── session:abc123    # User's session (inherits from user:456)
└── custom:project-x      # Custom namespace
```

### Private Computation

The `EXECUTE` permission enables blind computation - agents can use values without seeing them:

```python
# Agent passes reference to tool
# Tool resolves with EXECUTE permission
# Agent never sees the actual value
@mcp.tool()
def process_secret(secret_ref: str) -> dict:
    secret = cache.resolve(secret_ref, permission=Permission.EXECUTE)
    return {"hash": hash(secret)}  # Agent sees result, not secret
```

## Repository Setup

### Branch Protection Rules

To ensure code quality and prevent accidental breakage, configure branch protection rules for the `main` branch.

#### Required Setup

Navigate to **Settings → Branches → Branch protection rules** and configure:

**1. Require a pull request before merging**
- ✅ Require approvals: 1+ (recommended for teams)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (optional, if using CODEOWNERS file)
- ✅ Require approval of the most recent reviewable push

**2. Require status checks to pass before merging**
- ✅ Require branches to be up to date before merging
- Required status checks (select all that apply):
  - `CI Success` ← **CRITICAL** (gates Release workflow)
  - `Lint & Format`
  - `Test (Python 3.12)`
  - `Test (Python 3.13)` (if testing multiple versions)
  - `Security Scan`
  - `Build Package` (if running in CI)

**3. Additional protections (recommended)**
- ✅ Require linear history (enforces rebase/squash merges)
- ✅ Require deployments to succeed before merging (if using environments)
- ✅ Do not allow bypassing the above settings (prevents admin bypasses)

**4. Rules applied to everyone**
- ✅ Include administrators (enforce rules for all users)

#### Why This Matters

Branch protection ensures:
- ✅ All code is reviewed before merging
- ✅ CI must pass before merge (prevents broken code in main)
- ✅ Release workflow only builds verified commits
- ✅ Docker images are only published for tested code
- ✅ PyPI packages are only published after images built

#### Workflow Chain

The CI-gated workflow ensures safe releases:

```
Feature Branch
    ↓
Open PR → CI Runs (lint, test, security)
    ↓
CI Passes ✅ (required by branch protection)
    ↓
Merge to main
    ↓
CI Re-runs on main
    ↓
Release Workflow waits for CI Success
    ↓
Docker Images Built & Pushed to GHCR
    ↓
Manually Create GitHub Release
    ↓
Publish Workflow verifies Release succeeded
    ↓
Package Published to PyPI
    ↓
CD Workflow deploys (staging/production)
```

**Key safeguards:**
- Tag pushes verify CI passed before building images
- Publish workflow verifies Release workflow succeeded
- CD workflow only deploys after Release completes

#### Testing Branch Protection

Verify your setup works:

1. Create a feature branch with a failing test
2. Open a PR → CI should fail
3. Attempt to merge → Should be blocked by branch protection
4. Fix the test, push changes
5. CI passes → Merge becomes available

## Questions?

Open an issue on GitHub or reach out to the maintainers.
