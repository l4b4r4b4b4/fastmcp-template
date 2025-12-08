#!/usr/bin/env python3
"""FastMCP Template Server with RefCache and Langfuse Tracing.

This template demonstrates how to use mcp-refcache with FastMCP to build
an MCP server that handles large results efficiently with full observability.

Features demonstrated:
- Reference-based caching for large results
- Preview generation (sample, truncate, paginate strategies)
- Pagination for accessing large datasets
- Access control (user vs agent permissions)
- Private computation (EXECUTE without READ)
- Both sync and async tool implementations
- **Langfuse tracing integration** for observability

Usage:
    # Install dependencies
    uv sync

    # Set Langfuse credentials (optional but recommended)
    export LANGFUSE_PUBLIC_KEY="pk-lf-..."
    export LANGFUSE_SECRET_KEY="sk-lf-..."

    # Run with stdio (for Claude Desktop / Zed)
    uv run fastmcp-template

    # Run with SSE (for web clients / debugging)
    uv run fastmcp-template --transport sse --port 8000

Claude Desktop Configuration:
    Add to your claude_desktop_config.json:
    {
        "mcpServers": {
            "fastmcp-template": {
                "command": "uv",
                "args": ["run", "fastmcp-template"]
            }
        }
    }
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Check for FastMCP availability
# =============================================================================

try:
    from fastmcp import FastMCP
except ImportError:
    print(
        "Error: FastMCP is not installed. Install with:\n  uv sync\n",
        file=sys.stderr,
    )
    sys.exit(1)

# =============================================================================
# Import mcp-refcache components
# =============================================================================

from mcp_refcache import (
    AccessPolicy,
    CacheResponse,
    DefaultActor,
    Permission,
    PreviewConfig,
    PreviewStrategy,
    RefCache,
)
from mcp_refcache.fastmcp import (
    cache_guide_prompt,
    cache_instructions,
    register_admin_tools,
    with_cache_docs,
)

# =============================================================================
# Import Langfuse tracing
# =============================================================================
from app.tracing import (
    MockContext,
    TracedRefCache,
    enable_test_mode,
    flush_traces,
    get_langfuse_attributes,
    is_langfuse_enabled,
    is_test_mode_enabled,
    traced_tool,
)

# =============================================================================
# Initialize FastMCP Server
# =============================================================================

mcp = FastMCP(
    name="FastMCP Template",
    instructions=f"""A template MCP server with reference-based caching and Langfuse tracing.

All tool calls are traced to Langfuse with:
- User ID and Session ID from context (for filtering/aggregation)
- Full context metadata (org_id, agent_id, cache_namespace)
- Cache operation spans with hit/miss tracking

Enable test mode with enable_test_context() to simulate different users.

Available tools:
- hello: Simple greeting tool (no caching)
- generate_items: Generate a list of items (cached in public namespace)
- store_secret: Store a secret value for private computation
- compute_with_secret: Use a secret in computation without revealing it
- get_cached_result: Retrieve or paginate through cached results
- enable_test_context: Enable/disable test context for Langfuse demos
- set_test_context: Set test context values for user attribution
- reset_test_context: Reset test context to defaults
- get_trace_info: Get current Langfuse tracing status

{cache_instructions()}
""",
)

# =============================================================================
# Initialize RefCache with Langfuse Tracing
# =============================================================================

# Create the base RefCache instance
_cache = RefCache(
    name="fastmcp-template",
    default_ttl=3600,  # 1 hour TTL
    preview_config=PreviewConfig(
        max_size=64,  # Max 64 tokens in previews
        default_strategy=PreviewStrategy.SAMPLE,  # Sample large collections
    ),
)

# Wrap with TracedRefCache for Langfuse observability
cache = TracedRefCache(_cache)

# =============================================================================
# Pydantic Models for Tool Inputs
# =============================================================================


class ItemGenerationInput(BaseModel):
    """Input model for item generation."""

    count: int = Field(
        default=10,
        ge=1,
        le=10000,
        description="Number of items to generate",
    )
    prefix: str = Field(
        default="item",
        description="Prefix for item names",
    )


class SecretInput(BaseModel):
    """Input model for storing secret values."""

    name: str = Field(
        description="Name for the secret (used as key)",
        min_length=1,
        max_length=100,
    )
    value: float = Field(
        description="The secret numeric value",
    )


class SecretComputeInput(BaseModel):
    """Input model for computing with secrets."""

    secret_ref: str = Field(
        description="Reference ID of the secret value",
    )
    multiplier: float = Field(
        default=1.0,
        description="Multiplier to apply to the secret value",
    )


class CacheQueryInput(BaseModel):
    """Input model for cache queries."""

    ref_id: str = Field(
        description="Reference ID to look up",
    )
    page: int | None = Field(
        default=None,
        ge=1,
        description="Page number for pagination (1-indexed)",
    )
    page_size: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="Number of items per page",
    )
    max_size: int | None = Field(
        default=None,
        ge=1,
        description="Maximum preview size (tokens/chars). Overrides defaults.",
    )


# =============================================================================
# Context Management Tools (for Langfuse attribution testing)
# =============================================================================


@mcp.tool
def enable_test_context(enabled: bool = True) -> dict[str, Any]:
    """Enable or disable test context mode for Langfuse attribution demos.

    When enabled, all traces will include user_id, session_id, and metadata
    from the MockContext. This allows testing Langfuse filtering and
    aggregation without a real FastMCP authentication setup.

    Args:
        enabled: Whether to enable test context mode (default: True).

    Returns:
        Status dict with current test mode state and context values.
    """
    enable_test_mode(enabled)

    if enabled:
        return {
            "test_mode": True,
            "context": MockContext.get_current_state(),
            "langfuse_enabled": is_langfuse_enabled(),
            "message": "Test context mode enabled. Traces will include user/session from MockContext.",
        }
    return {
        "test_mode": False,
        "context": None,
        "langfuse_enabled": is_langfuse_enabled(),
        "message": "Test context mode disabled. Context will come from real FastMCP.",
    }


@mcp.tool
def set_test_context(
    user_id: str | None = None,
    org_id: str | None = None,
    session_id: str | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Set test context values for Langfuse attribution demos.

    Changes here affect what user_id, session_id, and metadata are
    sent to Langfuse traces. Use this to test filtering by different
    users or sessions in the Langfuse dashboard.

    Args:
        user_id: User identity (e.g., "alice", "bob").
        org_id: Organization identity (e.g., "acme", "globex").
        session_id: Session identifier for grouping traces.
        agent_id: Agent identity (e.g., "claude", "gpt4").

    Returns:
        Updated context state and example of Langfuse attributes.
    """
    # Auto-enable test mode when setting context
    if not is_test_mode_enabled():
        enable_test_mode(True)

    if user_id is not None:
        MockContext.set_state(user_id=user_id)
    if org_id is not None:
        MockContext.set_state(org_id=org_id)
    if agent_id is not None:
        MockContext.set_state(agent_id=agent_id)
    if session_id is not None:
        MockContext.set_session_id(session_id)

    # Show what Langfuse will receive
    attributes = get_langfuse_attributes()

    return {
        "context": MockContext.get_current_state(),
        "langfuse_attributes": {
            "user_id": attributes["user_id"],
            "session_id": attributes["session_id"],
            "metadata": attributes["metadata"],
            "tags": attributes["tags"],
        },
        "message": "Context updated. Next tool calls will use these Langfuse attributes.",
    }


@mcp.tool
def reset_test_context() -> dict[str, Any]:
    """Reset test context to default demo values.

    Returns:
        Reset context state.
    """
    MockContext.reset()
    return {
        "context": MockContext.get_current_state(),
        "message": "Context reset to default demo values.",
    }


@mcp.tool
def get_trace_info() -> dict[str, Any]:
    """Get information about the current Langfuse trace and context.

    Returns metadata about Langfuse tracing status and current
    context values for debugging.

    Returns:
        Dict with Langfuse configuration and current context.
    """
    import os

    attributes = get_langfuse_attributes()

    return {
        "langfuse_enabled": is_langfuse_enabled(),
        "langfuse_host": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        "public_key_set": bool(os.getenv("LANGFUSE_PUBLIC_KEY")),
        "secret_key_set": bool(os.getenv("LANGFUSE_SECRET_KEY")),
        "test_mode_enabled": is_test_mode_enabled(),
        "current_context": MockContext.get_current_state()
        if is_test_mode_enabled()
        else None,
        "langfuse_attributes": {
            "user_id": attributes["user_id"],
            "session_id": attributes["session_id"],
            "metadata": attributes["metadata"],
            "tags": attributes["tags"],
        },
        "message": (
            "Traces are being sent to Langfuse with user/session attribution"
            if is_langfuse_enabled()
            else "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable tracing"
        ),
    }


# =============================================================================
# Tool Implementations with Langfuse Tracing
# =============================================================================


@mcp.tool
@traced_tool("hello")
def hello(name: str = "World") -> dict[str, Any]:
    """Say hello to someone.

    A simple example tool that doesn't use caching.
    Traced to Langfuse with user/session attribution.

    Args:
        name: The name to greet.

    Returns:
        A greeting message.
    """
    return {
        "message": f"Hello, {name}!",
        "server": "fastmcp-template",
    }


@mcp.tool
@cache.cached(namespace="public")
async def generate_items(
    count: int = 10,
    prefix: str = "item",
) -> dict[str, Any]:
    """Generate a list of items.

    Demonstrates caching of large results in the PUBLIC namespace.
    For large counts, returns a reference with a preview instead of the full data.
    All operations are traced to Langfuse with user/session attribution.

    Use get_cached_result to paginate through large results.

    Args:
        count: Number of items to generate.
        prefix: Prefix for item names.

    Returns:
        List of items with id, name, and value.

    **Caching:** Large results are cached in the public namespace.

    **Pagination:** Use `page` and `page_size` to navigate results.

    **Preview Size:** server default. Override per-call with `get_cached_result(ref_id, max_size=...)`
    """
    validated = ItemGenerationInput(count=count, prefix=prefix)

    items = [
        {
            "id": i,
            "name": f"{validated.prefix}_{i}",
            "value": i * 10,
        }
        for i in range(validated.count)
    ]

    # Return raw data - decorator handles caching and structured response
    return items


@mcp.tool
@traced_tool("store_secret")
def store_secret(name: str, value: float) -> dict[str, Any]:
    """Store a secret value that agents cannot read, only use in computations.

    This demonstrates the EXECUTE permission - agents can use the value
    in compute_with_secret without ever seeing what it is.
    Traced to Langfuse (secret value is NOT logged).

    Args:
        name: Name for the secret.
        value: The secret numeric value.

    Returns:
        Reference ID and confirmation message.
    """
    validated = SecretInput(name=name, value=value)

    # Create a policy where agents can EXECUTE but not READ
    secret_policy = AccessPolicy(
        user_permissions=Permission.FULL,  # Users can see everything
        agent_permissions=Permission.EXECUTE,  # Agents can only use in computation
    )

    ref = cache.set(
        key=f"secret_{validated.name}",
        value=validated.value,
        namespace="user:secrets",
        policy=secret_policy,
        tool_name="store_secret",
    )

    return {
        "ref_id": ref.ref_id,
        "name": validated.name,
        "message": f"Secret '{validated.name}' stored. Use compute_with_secret to use it.",
        "permissions": {
            "user": "FULL (can read, write, execute)",
            "agent": "EXECUTE only (can use in computation, cannot read)",
        },
    }


@mcp.tool
@with_cache_docs(accepts_references=True, private_computation=True)
@traced_tool("compute_with_secret")
def compute_with_secret(secret_ref: str, multiplier: float = 1.0) -> dict[str, Any]:
    """Compute using a secret value without revealing it.

    The secret is multiplied by the provided multiplier.
    This demonstrates private computation - the agent orchestrates
    the computation but never sees the actual secret value.
    Traced to Langfuse (computation logged, secret value NOT exposed).

    Args:
        secret_ref: Reference ID of the secret value.
        multiplier: Value to multiply the secret by.

    Returns:
        The computation result (without revealing the secret).

    **References:** This tool accepts `ref_id` from previous tool calls.

    **Private Compute:** Values are processed server-side without exposure.
    """
    validated = SecretComputeInput(secret_ref=secret_ref, multiplier=multiplier)

    # Create a system actor to resolve the secret (bypasses agent restrictions)
    system_actor = DefaultActor.system()

    try:
        # Resolve the secret value as system (has full access)
        secret_value = cache.resolve(validated.secret_ref, actor=system_actor)
    except KeyError as e:
        raise ValueError(f"Secret reference '{validated.secret_ref}' not found") from e

    result = secret_value * validated.multiplier

    return {
        "result": result,
        "multiplier": validated.multiplier,
        "secret_ref": validated.secret_ref,
        "message": "Computed using secret value (value not revealed)",
    }


@mcp.tool
@with_cache_docs(accepts_references=True, supports_pagination=True)
@traced_tool("get_cached_result")
async def get_cached_result(
    ref_id: str,
    page: int | None = None,
    page_size: int | None = None,
    max_size: int | None = None,
) -> dict[str, Any]:
    """Retrieve a cached result, optionally with pagination.

    Use this to:
    - Get a preview of a cached value
    - Paginate through large lists
    - Access the full value of a cached result

    All cache operations are traced to Langfuse with hit/miss status.

    Args:
        ref_id: Reference ID to look up.
        page: Page number (1-indexed).
        page_size: Items per page.
        max_size: Maximum preview size (overrides defaults).

    Returns:
        The cached value or a preview with pagination info.

    **Caching:** Large results are returned as references with previews.

    **Pagination:** Use `page` and `page_size` to navigate results.

    **References:** This tool accepts `ref_id` from previous tool calls.
    """
    validated = CacheQueryInput(
        ref_id=ref_id, page=page, page_size=page_size, max_size=max_size
    )

    try:
        response: CacheResponse = cache.get(
            validated.ref_id,
            page=validated.page,
            page_size=validated.page_size,
            actor="agent",
        )

        result: dict[str, Any] = {
            "ref_id": validated.ref_id,
            "preview": response.preview,
            "preview_strategy": response.preview_strategy.value,
            "total_items": response.total_items,
        }

        if response.page is not None:
            result["page"] = response.page
            result["total_pages"] = response.total_pages

        if response.original_size:
            result["original_size"] = response.original_size
            result["preview_size"] = response.preview_size

        return result

    except (PermissionError, KeyError):
        return {
            "error": "Invalid or inaccessible reference",
            "message": "Reference not found, expired, or access denied",
            "ref_id": validated.ref_id,
        }


# =============================================================================
# Health Check
# =============================================================================


@mcp.tool
@traced_tool("health_check")
def health_check() -> dict[str, Any]:
    """Check server health status.

    Returns:
        Health status information including Langfuse tracing status.
    """
    return {
        "status": "healthy",
        "server": "fastmcp-template",
        "cache": cache.name,
        "langfuse_enabled": is_langfuse_enabled(),
        "test_mode": is_test_mode_enabled(),
    }


# =============================================================================
# Admin Tools (Permission-Gated)
# =============================================================================


async def is_admin(ctx: Any) -> bool:
    """Check if the current context has admin privileges.

    Override this in your own server with proper auth logic.
    """
    # Demo: No admin access by default
    return False


# Register admin tools with the underlying cache (not the traced wrapper)
_admin_tools = register_admin_tools(
    mcp,
    _cache,
    admin_check=is_admin,
    prefix="admin_",
    include_dangerous=False,
)


# =============================================================================
# Prompts for Guidance
# =============================================================================


@mcp.prompt
def template_guide() -> str:
    """Guide for using this MCP server template."""
    return f"""# FastMCP Template Guide

## Langfuse Tracing

All tool calls are traced to Langfuse with user/session attribution.

1. **Enable Test Mode**
   ```
   enable_test_context(True)
   ```

2. **Set User Context**
   ```
   set_test_context(user_id="alice", org_id="acme", session_id="chat-001")
   ```

3. **View Trace Info**
   ```
   get_trace_info()
   ```

4. **View in Langfuse Dashboard**
   - Filter by User: "alice"
   - Filter by Session: "chat-001"
   - Filter by Tags: "fastmcptemplate", "mcprefcache"

## Quick Start

1. **Simple Tool**
   Use `hello` for a basic greeting:
   - `hello("World")` → "Hello, World!"

2. **Generate Items (Caching Demo)**
   Use `generate_items` to create a list:
   - `generate_items(count=100, prefix="widget")`
   - Returns ref_id + preview for large results
   - Cached in the PUBLIC namespace (shared)

3. **Paginate Results**
   Use `get_cached_result` to navigate large results:
   - `get_cached_result(ref_id, page=2, page_size=20)`

## Private Computation

Store values that agents can use but not see:

```
# Store a secret
store_secret("api_key_hash", 12345.0)
# Returns ref_id for the secret

# Use in computation (agent never sees the value)
compute_with_secret(ref_id, multiplier=2.0)
# Returns the result
```

---

{cache_guide_prompt()}
"""


@mcp.prompt
def langfuse_guide() -> str:
    """Guide for using Langfuse tracing with this server."""
    return """# Langfuse Tracing Guide

## Setup

Set environment variables before starting the server:

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"  # Optional, defaults to cloud
```

## Context Propagation

All tool calls automatically propagate context to Langfuse traces:

1. **User Attribution**
   - `user_id`: Tracks which user made the request
   - `session_id`: Groups related requests into sessions
   - `metadata`: Additional context (org_id, agent_id, cache_namespace)

2. **Testing Context**
   Enable test mode to simulate different users:
   ```
   enable_test_context(True)
   set_test_context(user_id="alice", org_id="acme", session_id="chat-001")
   ```

3. **Cache Operations**
   Cache set/get/resolve operations create child spans that inherit
   user_id and session_id for complete attribution.

## Example Workflow

```python
# 1. Enable test mode and set user
enable_test_context(True)
set_test_context(user_id="alice", session_id="demo-session")

# 2. Generate items (traced with user attribution)
result = generate_items(count=100, prefix="widget")

# 3. Retrieve cached result (same user in trace)
cached = get_cached_result(result["ref_id"])

# 4. Check trace info
info = get_trace_info()
```

## Viewing Traces in Langfuse

1. Go to your Langfuse dashboard
2. Navigate to Traces
3. Filter by:
   - **User**: "alice" (or any user_id you set)
   - **Session**: "demo-session"
   - **Tags**: "fastmcptemplate", "mcprefcache", "cacheset", "cacheget"
   - **Metadata**: orgid, agentid, cachenamespace

## Best Practices

- Enable test mode for demos and testing
- Use meaningful user_id and session_id values
- Check get_trace_info() to verify tracing is working
- Flush traces on server shutdown (handled automatically)
"""


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> None:
    """Run the MCP server."""
    parser = argparse.ArgumentParser(
        description="FastMCP Template Server with RefCache and Langfuse Tracing",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode (default: stdio for Claude Desktop)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for SSE transport (default: 127.0.0.1)",
    )

    args = parser.parse_args()

    # Print startup info
    print(f"Langfuse tracing: {'enabled' if is_langfuse_enabled() else 'disabled'}")
    print("Context propagation: enabled (user_id, session_id, metadata)")
    print("Use enable_test_context() to simulate different users")

    try:
        if args.transport == "stdio":
            mcp.run(transport="stdio")
        else:
            mcp.run(
                transport="sse",
                host=args.host,
                port=args.port,
            )
    finally:
        # Ensure all traces are flushed on exit
        flush_traces()


if __name__ == "__main__":
    main()
