{%- set use_demo_tools = (cookiecutter.template_variant == 'full') or (cookiecutter.template_variant == 'custom' and cookiecutter.include_demo_tools == 'yes') -%}
{%- set use_secret_tools = (cookiecutter.template_variant == 'full') or (cookiecutter.template_variant == 'custom' and cookiecutter.include_secret_tools == 'yes') -%}
{%- set use_langfuse = (cookiecutter.template_variant in ['standard', 'full']) or (cookiecutter.template_variant == 'custom' and cookiecutter.include_langfuse == 'yes') -%}
"""Tools module for {{ cookiecutter.project_name }}.

This module re-exports all tools from submodules for convenient access.

Tool Modules:
{% if use_demo_tools %}
- demo: Simple demonstration tools (hello, generate_items)
{% endif %}
- context: Langfuse test context management
{% if use_secret_tools %}
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
{% if use_demo_tools %}
from app.tools.demo import ItemGenerationInput, generate_items, hello
{% endif %}
from app.tools.health import create_health_check
{% if use_secret_tools %}
from app.tools.secrets import (
    SecretComputeInput,
    SecretInput,
    create_compute_with_secret,
    create_store_secret,
)
{% endif %}

__all__ = [
    "CacheQueryInput",
{% if use_demo_tools %}
    "ItemGenerationInput",
{% endif %}
{% if use_secret_tools %}
    "SecretComputeInput",
    "SecretInput",
    "create_compute_with_secret",
{% endif %}
    "create_get_cached_result",
    "create_health_check",
{% if use_secret_tools %}
    "create_store_secret",
{% endif %}
    "enable_test_context",
{% if use_demo_tools %}
    "generate_items",
{% endif %}
    "get_trace_info",
{% if use_demo_tools %}
    "hello",
{% endif %}
    "reset_test_context",
    "set_test_context",
]
