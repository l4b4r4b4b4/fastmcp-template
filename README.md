# FastMCP Cookiecutter Template

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

### Minimal Project (No Demo Tools)

Perfect for starting fresh:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# When prompted:
include_demo_tools [no]: <press Enter>
```

Generates a clean project with no example tools - ready for your implementation.

### Learning Project (With Demo Tools)

Includes reference implementations:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# When prompted:
include_demo_tools [no]: yes
```

Includes working examples:
- `hello` - Basic tool pattern
- `generate_items` - Cached large data with RefCache
- `store_secret` / `compute_with_secret` - Private computation pattern

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