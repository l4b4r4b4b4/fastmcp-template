"""Cache query and retrieval tools.

This module provides tools for querying and retrieving cached results,
with support for pagination and preview customization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from app.tracing import traced_tool

if TYPE_CHECKING:
    from mcp_refcache import RefCache


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


def create_get_cached_result(cache: RefCache) -> Any:
    """Create a get_cached_result tool function bound to the given cache.

    Args:
        cache: The RefCache instance to use for cache lookups.

    Returns:
        The get_cached_result tool function.
    """

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
            ref_id=ref_id,
            page=page,
            page_size=page_size,
            max_size=max_size,
        )

        try:
            response = cache.get(
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

    return get_cached_result


__all__ = [
    "CacheQueryInput",
    "create_get_cached_result",
]
