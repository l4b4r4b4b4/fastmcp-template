"""Health check tools for FastMCP Template Server.

This module provides health check functionality for monitoring
server status and verifying tracing configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.tracing import is_langfuse_enabled, is_test_mode_enabled, traced_tool

if TYPE_CHECKING:
    from mcp_refcache import RefCache


def create_health_check(cache: RefCache) -> Any:
    """Create a health_check tool function bound to the given cache.

    Args:
        cache: The RefCache instance to report on.

    Returns:
        The health_check tool function.
    """

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

    return health_check


__all__ = [
    "create_health_check",
]
