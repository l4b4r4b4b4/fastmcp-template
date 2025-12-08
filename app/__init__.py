"""FastMCP Template - FastMCP server with mcp-refcache and Langfuse tracing."""

from importlib.metadata import version

# Package name must match [project].name in pyproject.toml
# This is the single source of truth for versioning
__version__ = version("fastmcp-template")

# Re-export tracing utilities for convenience
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

__all__ = [
    "MockContext",
    "TracedRefCache",
    "__version__",
    "enable_test_mode",
    "flush_traces",
    "get_langfuse_attributes",
    "is_langfuse_enabled",
    "is_test_mode_enabled",
    "traced_tool",
]
