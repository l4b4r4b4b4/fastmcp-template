# FastMCP Cookiecutter Template

[![Template CI](https://github.com/l4b4r4b4b4/fastmcp-template/actions/workflows/test-template.yml/badge.svg)](https://github.com/l4b4r4b4b4/fastmcp-template/actions/workflows/test-template.yml)
[![Template Verified](https://img.shields.io/badge/Template-4%2F4%20Configs%20Verified-success?style=flat-square&logo=checkmarx&logoColor=white)](VERIFICATION.md)
[![Last Verified](https://img.shields.io/badge/Last%20Verified-Jan%202025-blue?style=flat-square&logo=calendar&logoColor=white)](VERIFICATION.md)
[![Tests Passing](https://img.shields.io/badge/Tests-346%2F346%20Passing-brightgreen?style=flat-square&logo=pytest&logoColor=white)](VERIFICATION.md)

🚀 Production-ready [FastMCP](https://github.com/jlowin/fastmcp) server template with [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache) integration for building AI agent tools that handle large data efficiently.

## Quick Start

### Using Cookiecutter

```bash
# Install cookiecutter (one-time)
uv tool install cookiecutter
# or: pipx install cookiecutter

# Generate your project
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# Follow the prompts:
# - project_name: Your MCP Server
# - project_slug: your-mcp-server (auto-generated)
# - project_description: What your server does
# - author_name: Your Name
# - author_email: you@example.com
# - python_version: 3.12 (default)
# - include_demo_tools: no (clean start) or yes (with examples)
# - include_secret_tools: no (minimal) or yes (with secret examples)
# - include_langfuse: yes (observability) or no
# - github_username: your-github-username

# Navigate to your new project
cd your-mcp-server

# Start developing!
uv run pytest
uv run your-mcp-server stdio
```

### What You Get

A fully-configured FastMCP server with:

- ✅ **Reference-Based Caching** - Handle large data without context window limits
- ✅ **Preview Generation** - Automatic previews for large results
- ✅ **Pagination** - Navigate datasets efficiently
- ✅ **Access Control** - Separate user/agent permissions
- ✅ **Private Computation** - Agents compute with values they cannot see
- ✅ **Docker Ready** - Production containers with multi-stage builds
- ✅ **GitHub Actions** - CI/CD with PyPI publishing and GHCR containers
- ✅ **Optional Langfuse** - Built-in observability integration
- ✅ **Type-Safe** - Full type hints with Pydantic models
- ✅ **Testing Ready** - pytest with 73% coverage requirement
- ✅ **Pre-commit Hooks** - Ruff formatting and linting

## Template Options

### Configuration Options

| Option | Default | Values | Purpose |
|--------|---------|--------|---------|
| `include_demo_tools` | `no` | `no`, `yes` | Include `hello` and `generate_items` demo tools |
| `include_secret_tools` | `no` | `no`, `yes` | Include `store_secret` and `compute_with_secret` examples |
| `include_langfuse` | `yes` | `yes`, `no` | Enable Langfuse tracing integration |

### Minimal Project (Recommended)

Perfect for starting fresh with only core infrastructure:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# When prompted:
include_demo_tools [no]: <press Enter>
include_secret_tools [no]: <press Enter>
```

Generates a clean project with:
- ✅ Health check tool
- ✅ Cache query tool
- ✅ Admin tools (permission-gated)
- ❌ No example/demo code

### Full Learning Project

Includes all reference implementations:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# When prompted:
include_demo_tools [no]: yes
include_secret_tools [no]: yes
```

Includes working examples:
- `hello` - Basic tool pattern
- `generate_items` - Cached large data with RefCache
- `store_secret` / `compute_with_secret` - Private computation pattern

### Custom Mix

Choose which examples to include:

```bash
# Only demo tools (no secrets)
include_demo_tools: yes
include_secret_tools: no

# Only secret tools (no demos)
include_demo_tools: no
include_secret_tools: yes
```

## Features

### Reference-Based Caching (RefCache)

Instead of returning large data directly, return a reference:

```python
@mcp.tool
@cache.cached(namespace="public")
async def fetch_large_dataset(query: str) -> list[dict]:
    """Fetch dataset - returns reference for large results."""
    data = await get_data(query)  # e.g., 10,000 rows
    return data  # RefCache automatically creates reference
```

Agent receives a reference instead of 10,000 rows in context window.

### Private Computation

Store sensitive values agents can compute with but not read:

```python
@mcp.tool
def store_secret(name: str, value: float) -> dict:
    """Store value with EXECUTE-only permission."""
    policy = AccessPolicy(
        user_permissions=Permission.FULL,
        agent_permissions=Permission.EXECUTE,  # Can use, cannot read
    )
    ref = cache.set(f"secret_{name}", value, policy=policy)
    return {"ref_id": ref.ref_id}

@mcp.tool
def compute_with_secret(secret_ref: str, multiplier: float) -> dict:
    """Compute using secret without revealing it."""
    secret = cache.resolve(secret_ref, actor=DefaultActor.system())
    return {"result": secret * multiplier}
```

## Project Structure

```
your-mcp-server/
├── app/                     # Application code
│   ├── server.py            # Main MCP server
│   ├── tools/               # Tool modules
│   └── __main__.py          # CLI entry point
├── tests/                   # Test suite
│   ├── conftest.py
│   └── test_server.py
├── docker/                  # Docker configurations
│   ├── Dockerfile.base      # Python base with dependencies
│   ├── Dockerfile           # Production image
│   └── Dockerfile.dev       # Development with hot reload
├── .github/workflows/       # CI/CD pipelines
│   ├── ci.yml               # Lint, test, security
│   ├── publish.yml          # PyPI publishing
│   └── release.yml          # Docker builds
├── .agent/                  # AI assistant workspace
│   └── goals/
│       └── 00-Template-Goal/  # Goal tracking template
├── pyproject.toml           # Project configuration
├── docker-compose.yml       # Local development
└── README.md                # Project documentation
```

## Next Steps After Generation

1. **Review the generated project**
   ```bash
   cd your-mcp-server
   cat README.md  # Project-specific documentation
   ```

2. **Run tests**
   ```bash
   uv run pytest
   ```

3. **Try the server**
   ```bash
   uv run your-mcp-server stdio
   ```

4. **Add your tools**
   - Create tool modules in `app/tools/`
   - Register in `app/server.py`
   - Add tests in `tests/`

5. **Configure GitHub publishing** (optional)
   - PyPI: Add trusted publisher at pypi.org
   - GHCR: GitHub Actions will publish on release

## Testing the Template

### Automated CI Testing

The template is automatically tested on every push and pull request. CI validates all 4 configurations:
- ✅ Minimal (no/no) - 74 tests
- ✅ Full (yes/yes) - 101 tests
- ✅ Demos Only (yes/no) - 86 tests
- ✅ Secrets Only (no/yes) - 85 tests

Each configuration is tested for:
- Successful project generation
- All tests passing
- Linting passes (ruff check)
- No hardcoded template values
- Correct test count

### Local Testing

Test a specific configuration before submitting changes:

```bash
# Test minimal configuration
./scripts/validate-template.sh minimal

# Test full configuration
./scripts/validate-template.sh full

# Test all configurations
./scripts/validate-template.sh --all
```

### Manual Verification

Generate and test a project manually:

```bash
# Generate project
uv run cookiecutter . --output-dir /tmp/test-project --no-input \
  project_name="Test Project" \
  include_demo_tools=yes \
  include_secret_tools=no

# Test generated project
cd /tmp/test-project/test-project
uv run pytest -v
uv run ruff check .
```

### Verification Report

See [VERIFICATION.md](VERIFICATION.md) for comprehensive manual testing results:
- Detailed test breakdowns for all configurations
- Manual verification of demo tools functionality
- Architecture notes and troubleshooting guides
- 346 total tests verified across all configurations

## Features in Detail
## Development

To work on the template itself (not generate projects):

```bash
git clone https://github.com/l4b4r4b4b4/fastmcp-template
cd fastmcp-template

# The actual template is in {{cookiecutter.project_slug}}/
ls "{{cookiecutter.project_slug}}/"

# Test template generation locally
cookiecutter . --no-input
# or
cookiecutter .  # With prompts
```

## Documentation

- **Template README**: See [`{{cookiecutter.project_slug}}/README.md`]({{cookiecutter.project_slug}}/README.md) for generated project documentation
- **FastMCP**: https://github.com/jlowin/fastmcp
- **mcp-refcache**: https://github.com/l4b4r4b4b4/mcp-refcache
- **MCP Protocol**: https://modelcontextprotocol.io/

## Contributing

See [CONTRIBUTING.md]({{cookiecutter.project_slug}}/CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE]({{cookiecutter.project_slug}}/LICENSE) for details.

## Related Projects

- [mcp-refcache](https://github.com/l4b4r4b4b4/mcp-refcache) - Reference-based caching for MCP servers
- [FastMCP](https://github.com/jlowin/fastmcp) - High-performance MCP framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - Protocol specification

---

**Generated with ❤️ using [Cookiecutter](https://github.com/cookiecutter/cookiecutter)**
