# FastMCP Template Documentation

This directory contains extended documentation for the FastMCP Template project.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastMCP Server                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Tools Layer                            │   │
│  │  ┌─────────┐ ┌──────────────┐ ┌─────────────────────┐    │   │
│  │  │  hello  │ │generate_items│ │ compute_with_secret │    │   │
│  │  └─────────┘ └──────────────┘ └─────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  mcp-refcache Layer                       │   │
│  │  ┌─────────────┐ ┌───────────────┐ ┌──────────────────┐  │   │
│  │  │  RefCache   │ │ AccessPolicy  │ │ PreviewStrategy  │  │   │
│  │  └─────────────┘ └───────────────┘ └──────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               Storage Backend (In-Memory)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Key Concepts

### Reference-Based Caching

Instead of returning large results directly (which would bloat the LLM context), mcp-refcache returns **references** with **previews**:

```python
# Large result (1000 items)
result = generate_items(count=1000)

# Returns:
{
    "ref_id": "public:abc123",
    "preview": [{"id": 0, "name": "item_0"}, {"id": 1, "name": "item_1"}, "..."],
    "total_items": 1000,
    "page": 1,
    "total_pages": 50
}
```

The agent sees a preview but can paginate through the full result using `get_cached_result`.

### Namespaces

Namespaces provide logical isolation for cached data:

| Namespace | Description | Use Case |
|-----------|-------------|----------|
| `public` | Shared across all users/sessions | Reference data, configurations |
| `user:{id}` | User-scoped data | User preferences, history |
| `session:{id}` | Session-scoped data | Temporary computation results |
| `user:secrets` | Private user data | Secrets, credentials |

### Access Control

The permission system distinguishes between **users** (humans) and **agents** (AI):

```python
from mcp_refcache import AccessPolicy, Permission

# Full access for users, execute-only for agents
secret_policy = AccessPolicy(
    user_permissions=Permission.FULL,
    agent_permissions=Permission.EXECUTE,
)
```

Permission levels:
- `NONE` - No access
- `READ` - Can read values
- `WRITE` - Can create/update values
- `EXECUTE` - Can use values in computation (without reading)
- `FULL` - All permissions

### Private Computation

The `EXECUTE` permission enables **blind computation** - agents can use values without seeing them:

```python
# 1. User stores a secret
store_secret("api_key", 12345.0)
# Returns: {"ref_id": "user:secrets:abc123", ...}

# 2. Agent uses the secret without seeing it
compute_with_secret("user:secrets:abc123", multiplier=2.0)
# Returns: {"result": 24690.0, ...}
# Agent never sees the original value (12345.0)
```

## Advanced Usage

### Adding New Tools

1. **Simple tool (no caching)**:
```python
@mcp.tool
def my_simple_tool(arg: str) -> dict:
    """Tool that returns small results directly."""
    return {"result": arg.upper()}
```

2. **Cached tool (large results)**:
```python
@mcp.tool
@cache.cached(namespace="public")
async def my_cached_tool(count: int = 100) -> list[dict]:
    """Tool that caches large results."""
    return [{"id": i} for i in range(count)]
```

3. **Tool with private computation**:
```python
@mcp.tool
@with_cache_docs(accepts_references=True, private_computation=True)
def my_private_tool(secret_ref: str) -> dict:
    """Tool that uses secrets without exposing them."""
    secret = cache.resolve(secret_ref, actor=DefaultActor.system())
    return {"hash": hash(secret)}
```

### Preview Strategies

Configure how large results are previewed:

```python
from mcp_refcache import PreviewConfig, PreviewStrategy

cache = RefCache(
    name="my-cache",
    preview_config=PreviewConfig(
        max_size=100,  # Max tokens in preview
        default_strategy=PreviewStrategy.SAMPLE,  # Sample items from list
    ),
)
```

Available strategies:
- `SAMPLE` - Show first N items from a sequence
- `TRUNCATE` - Truncate string/text content
- `PAGINATE` - Return a specific page of results
- `SUMMARIZE` - Provide a summary (requires custom implementation)

### Custom Admin Checks

Override the admin check for production:

```python
async def is_admin(ctx: Any) -> bool:
    """Check if the current context has admin privileges."""
    # Example: Check a header or token
    if hasattr(ctx, 'request'):
        token = ctx.request.headers.get('X-Admin-Token')
        return token == os.environ.get('ADMIN_TOKEN')
    return False

_admin_tools = register_admin_tools(
    mcp,
    cache,
    admin_check=is_admin,
    prefix="admin_",
    include_dangerous=True,  # Include destructive tools
)
```

### Langfuse Integration

Enable observability with Langfuse (optional):

```bash
# Install with Langfuse support
uv add langfuse
```

```python
import os
from langfuse import Langfuse

# Set environment variables
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-..."

# Langfuse client
langfuse = Langfuse()

# Trace tool calls
@mcp.tool
def traced_tool(arg: str) -> dict:
    trace = langfuse.trace(name="traced_tool", input={"arg": arg})
    result = {"processed": arg}
    trace.update(output=result)
    return result
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FASTMCP_TEMPLATE_DEBUG` | Enable debug logging | `false` |
| `FASTMCP_TEMPLATE_CACHE_TTL` | Default cache TTL (seconds) | `3600` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | - |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | - |

### CLI Options

```bash
# Run with stdio (default, for Claude Desktop)
uv run fastmcp-template

# Run with SSE (for web clients)
uv run fastmcp-template --transport sse --port 8000 --host 0.0.0.0
```

## Docker Deployment

### Image Architecture

The project provides three Docker configurations:

| Image | Base | Use Case |
|-------|------|----------|
| `fastmcp-base` | Chainguard Python | Secure base for all FastMCP servers |
| `fastmcp-template` | fastmcp-base | This template application |
| `fastmcp-template:dev` | python:3.12-slim | Development with hot reload |

### Why Chainguard?

[Chainguard](https://www.chainguard.dev/) images are security-hardened:
- **No shell** - Minimal attack surface
- **Daily CVE patches** - Fast security updates
- **Signed images** - Verified with Sigstore/cosign
- **Wolfi-based** - Purpose-built for containers
- **SBOMs included** - Software Bill of Materials for compliance

### Building Images

```bash
# Build base image (reusable for other FastMCP servers)
docker build -f docker/Dockerfile.base -t fastmcp-base:latest .

# Build app image
docker build -f docker/Dockerfile -t fastmcp-template:latest .

# Build dev image
docker build -f docker/Dockerfile.dev -t fastmcp-template:dev .
```

### Running Containers

```bash
# Production mode
docker run -p 8000:8000 fastmcp-template:latest

# With Langfuse tracing
docker run -p 8000:8000 \
  -e LANGFUSE_PUBLIC_KEY=pk-... \
  -e LANGFUSE_SECRET_KEY=sk-... \
  fastmcp-template:latest

# Development mode with hot reload
docker run -p 8000:8000 -v $(pwd)/app:/app/app:ro fastmcp-template:dev
```

### Docker Compose

```bash
# Production
docker compose up

# Development with hot reload
docker compose --profile dev up

# Build all images
docker compose build
```

### Extending the Base Image

Create your own FastMCP server by extending the base:

```dockerfile
FROM ghcr.io/l4b4r4b4b4/fastmcp-base:latest

# Copy your application
COPY app/ /app/app/

# Set your entrypoint
CMD ["python", "-m", "app.server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
```

### Publishing to GHCR

The GitHub Actions workflow automatically builds and publishes images:

```yaml
# Triggered on push to main or version tags
# Images published to:
#   ghcr.io/l4b4r4b4b4/fastmcp-base:latest
#   ghcr.io/l4b4r4b4b4/fastmcp-template:latest
```

## Troubleshooting

### Common Issues

**"FastMCP is not installed"**
```bash
uv sync  # Install dependencies
```

**"Reference not found"**
- Check that the ref_id is correct
- References expire after TTL (default: 1 hour)
- Check namespace permissions

**"Permission denied"**
- Verify the actor has required permissions
- Check the AccessPolicy on the cached value

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Further Reading

- [mcp-refcache Documentation](https://github.com/l4b4r4b4b4/mcp-refcache)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
