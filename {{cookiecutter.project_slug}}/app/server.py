{%- set use_demo_tools = (cookiecutter.template_variant == 'full') or (cookiecutter.template_variant == 'custom' and cookiecutter.include_demo_tools == 'yes') -%}
{%- set use_secret_tools = (cookiecutter.template_variant == 'full') or (cookiecutter.template_variant == 'custom' and cookiecutter.include_secret_tools == 'yes') -%}
{%- set use_langfuse = (cookiecutter.template_variant in ['standard', 'full']) or (cookiecutter.template_variant == 'custom' and cookiecutter.include_langfuse == 'yes') -%}
"""{{ cookiecutter.project_name }} - FastMCP Server with RefCache{% if use_langfuse %} and Langfuse Tracing{% endif %}.

This module creates and configures the FastMCP server, wiring together
tools from the modular tools package.

Features:
- Reference-based caching for large results
- Preview generation (sample, truncate, paginate strategies)
- Pagination for accessing large datasets
- Access control (user vs agent permissions)
- Private computation (EXECUTE without READ)
{% if use_langfuse %}
- Langfuse tracing integration for observability
{% endif %}

Usage:
    # Run with typer CLI
    uvx {{ cookiecutter.project_slug }} stdio           # Local CLI mode
    uvx {{ cookiecutter.project_slug }} streamable-http # Remote/Docker mode

    # Or with uv
    uv run {{ cookiecutter.project_slug }} stdio
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from mcp_refcache import PreviewConfig, PreviewStrategy, RefCache
from mcp_refcache.fastmcp import cache_instructions, register_admin_tools

from app.prompts import langfuse_guide, template_guide
from app.tools import (
    create_get_cached_result,
    create_health_check,
{% if use_secret_tools %}
    create_compute_with_secret,
    create_store_secret,
{% endif %}
{% if use_langfuse %}
    enable_test_context,
    get_trace_info,
    reset_test_context,
    set_test_context,
{% endif %}
{% if use_demo_tools %}
    generate_items,
    hello,
{% endif %}
)
{% if use_langfuse %}
from app.tracing import TracedRefCache
{% endif %}

# =============================================================================
# Initialize FastMCP Server
# =============================================================================

mcp = FastMCP(
    name="{{ cookiecutter.project_name }}",
    instructions=f"""{{ cookiecutter.project_description }}

{% if use_langfuse %}
All tool calls are traced to Langfuse with:
- User ID and Session ID from context (for filtering/aggregation)
- Full context metadata (org_id, agent_id, cache_namespace)
- Cache operation spans with hit/miss tracking

Enable test mode with enable_test_context() to simulate different users.

{% endif %}
Available tools:
{% if use_demo_tools %}
- hello: Simple greeting tool (no caching)
- generate_items: Generate a list of items (cached in public namespace)
{% endif %}
{% if use_secret_tools %}
- store_secret: Store a secret value for private computation
- compute_with_secret: Use a secret in computation without revealing it
{% endif %}
- get_cached_result: Retrieve or paginate through cached results
{% if use_langfuse %}
- enable_test_context: Enable/disable test context for Langfuse demos
- set_test_context: Set test context values for user attribution
- reset_test_context: Reset test context to defaults
- get_trace_info: Get current Langfuse tracing status
{% endif %}

{cache_instructions()}
""",
)

# =============================================================================
# Initialize RefCache{% if use_langfuse %} with Langfuse Tracing{% endif %}

# =============================================================================

# Create the base RefCache instance
_cache = RefCache(
    name="{{ cookiecutter.project_slug }}",
    default_ttl=3600,  # 1 hour TTL
    preview_config=PreviewConfig(
        max_size=2048,  # Max 2048 tokens in previews
        default_strategy=PreviewStrategy.SAMPLE,  # Sample large collections
    ),
)

{% if use_langfuse %}
# Wrap with TracedRefCache for Langfuse observability
cache = TracedRefCache(_cache)
{% else %}
# Use RefCache directly (no tracing)
cache = _cache
{% endif %}

# =============================================================================
# Create Bound Tool Functions
# =============================================================================

# These are created with factory functions and bound to the cache instance.
# We keep references for testing and re-export them as module attributes.
{% if use_secret_tools %}
store_secret = create_store_secret(cache)
compute_with_secret = create_compute_with_secret(cache)
{% endif %}
get_cached_result = create_get_cached_result(cache)
health_check = create_health_check(_cache)

# =============================================================================
# Register Tools
# =============================================================================

{% if use_demo_tools %}
# Demo tools
mcp.tool(hello)


@mcp.tool
@cache.cached(namespace="public")
async def _generate_items(
    count: int = 10,
    prefix: str = "item",
) -> dict[str, Any]:
    """Generate a list of items.

    Demonstrates caching of large results in the PUBLIC namespace.
    For large counts, returns a reference with a preview instead of the full data.
{% if use_langfuse %}
    All operations are traced to Langfuse with user/session attribution.
{% endif %}

    Use get_cached_result to paginate through large results.

    Args:
        count: Number of items to generate.
        prefix: Prefix for item names.

    Returns:
        List of items with id, name, and value.

    **Caching:** Large results are cached in the public namespace.

    **Pagination:** Use `page` and `page_size` to navigate results.

    **Preview Size:** server default. Override per-call with
        `get_cached_result(ref_id, max_size=...)`
    """
    items = await generate_items(count=count, prefix=prefix)
    return items  # type: ignore[return-value]  # decorator transforms to dict


{% endif %}
{% if use_langfuse %}
# Context management tools
mcp.tool(enable_test_context)
mcp.tool(set_test_context)
mcp.tool(reset_test_context)
mcp.tool(get_trace_info)

{% endif %}
# Cache-bound tools (using pre-created module-level functions)
{% if use_secret_tools %}
mcp.tool(store_secret)
mcp.tool(compute_with_secret)
{% endif %}
mcp.tool(get_cached_result)
mcp.tool(health_check)

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
# Register Prompts
# =============================================================================


@mcp.prompt
def _template_guide() -> str:
    """Guide for using this MCP server template."""
    return template_guide()

{% if use_langfuse %}

@mcp.prompt
def _langfuse_guide() -> str:
    """Guide for using Langfuse tracing with this server."""
    return langfuse_guide()
{% endif %}
