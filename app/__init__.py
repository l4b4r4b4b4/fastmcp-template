"""FastMCP Template - FastMCP server with mcp-refcache and Langfuse tracing."""

from importlib.metadata import PackageNotFoundError, version

# Package name must match [project].name in pyproject.toml
# This is the single source of truth for versioning
# Falls back to "0.0.0-dev" when running from source (e.g., Docker with copied files)
try:
    __version__ = version("fastmcp-template")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

# Re-export config for convenience
from app.config import Settings, get_settings, settings

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
    "Settings",
    "TracedRefCache",
    "__version__",
    "enable_test_mode",
    "flush_traces",
    "get_langfuse_attributes",
    "get_settings",
    "is_langfuse_enabled",
    "is_test_mode_enabled",
    "settings",
    "traced_tool",
]
