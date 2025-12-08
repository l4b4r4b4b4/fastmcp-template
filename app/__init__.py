"""FastMCP Template - FastMCP server with mcp-refcache and Langfuse tracing."""

from importlib.metadata import version

# Package name must match [project].name in pyproject.toml
# This is the single source of truth for versioning
__version__ = version("fastmcp-template")

__all__ = ["__version__"]
