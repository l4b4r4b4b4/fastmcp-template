"""Tools module for FastMCP Template Server.

This module re-exports all tools from submodules for convenient access.

Tool Modules:
- demo: Simple demonstration tools (hello, generate_items)
- context: Langfuse test context management
- secrets: Private computation with secrets
- cache: Cache query and retrieval
- health: Health check functionality
"""

from __future__ import annotations

from app.tools.cache import CacheQueryInput, create_get_cached_result
from app.tools.context import (
    enable_test_context,
    get_trace_info,
    reset_test_context,
    set_test_context,
)
from app.tools.demo import ItemGenerationInput, generate_items, hello
from app.tools.health import create_health_check
from app.tools.secrets import (
    SecretComputeInput,
    SecretInput,
    create_compute_with_secret,
    create_store_secret,
)

__all__ = [
    "CacheQueryInput",
    "ItemGenerationInput",
    "SecretComputeInput",
    "SecretInput",
    "create_compute_with_secret",
    "create_get_cached_result",
    "create_health_check",
    "create_store_secret",
    "enable_test_context",
    "generate_items",
    "get_trace_info",
    "hello",
    "reset_test_context",
    "set_test_context",
]
