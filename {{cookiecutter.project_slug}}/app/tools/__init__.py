"""Tools module for {{ cookiecutter.project_name }}.

This module re-exports all tools from submodules for convenient access.

Tool Modules:
{% if cookiecutter.include_demo_tools == "yes" %}
- demo: Simple demonstration tools (hello, generate_items)
{% endif %}
- context: Langfuse test context management
{% if cookiecutter.include_secret_tools == "yes" %}
- secrets: Private computation with secrets
{% endif %}
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
{% if cookiecutter.include_demo_tools == "yes" %}
from app.tools.demo import ItemGenerationInput, generate_items, hello
{% endif %}
from app.tools.health import create_health_check
{% if cookiecutter.include_secret_tools == "yes" %}
from app.tools.secrets import (
    SecretComputeInput,
    SecretInput,
    create_compute_with_secret,
    create_store_secret,
)
{% endif %}

__all__ = [
    "CacheQueryInput",
{% if cookiecutter.include_demo_tools == "yes" %}
    "ItemGenerationInput",
{% endif %}
{% if cookiecutter.include_secret_tools == "yes" %}
    "SecretComputeInput",
    "SecretInput",
    "create_compute_with_secret",
{% endif %}
    "create_get_cached_result",
    "create_health_check",
{% if cookiecutter.include_secret_tools == "yes" %}
    "create_store_secret",
{% endif %}
    "enable_test_context",
{% if cookiecutter.include_demo_tools == "yes" %}
    "generate_items",
{% endif %}
    "get_trace_info",
{% if cookiecutter.include_demo_tools == "yes" %}
    "hello",
{% endif %}
    "reset_test_context",
    "set_test_context",
]
