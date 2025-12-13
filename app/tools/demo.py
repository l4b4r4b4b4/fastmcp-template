"""Demo tools for FastMCP Template Server.

This module contains simple demonstration tools that showcase
basic MCP tool patterns and caching functionality.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.tracing import traced_tool


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


async def generate_items(
    count: int = 10,
    prefix: str = "item",
) -> list[dict[str, Any]]:
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

    Note:
        This function returns raw data. The @cache.cached decorator
        (applied in server.py) handles caching and structured responses.

    **Caching:** Large results are cached in the public namespace.

    **Pagination:** Use `page` and `page_size` to navigate results.

    **Preview Size:** server default. Override per-call with
        `get_cached_result(ref_id, max_size=...)`
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

    return items


__all__ = [
    "ItemGenerationInput",
    "generate_items",
    "hello",
]
