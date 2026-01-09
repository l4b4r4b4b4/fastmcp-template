"""Langfuse tracing integration for FastMCP Template.

This module provides Langfuse observability integration for mcp-refcache,
enabling comprehensive tracing of cache operations in MCP tools.

Features:
- TracedRefCache: A wrapper that adds Langfuse spans to cache operations
- Context extraction for user/session attribution
- MockContext for testing without real FastMCP auth
- Automatic trace propagation to child spans

Prerequisites:
    Set environment variables:
        LANGFUSE_PUBLIC_KEY=pk-lf-...
        LANGFUSE_SECRET_KEY=sk-lf-...
        LANGFUSE_HOST=https://cloud.langfuse.com  # or self-hosted URL

Langfuse SDK v3 Best Practices:
    - Use propagate_attributes() to pass user_id, session_id, metadata to ALL child spans
    - Call propagate_attributes() early in the trace for complete coverage
    - Metadata keys must be alphanumeric only (no spaces/special chars)
    - Values must be strings ≤200 characters
"""

from __future__ import annotations

import asyncio
import functools
import os
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar, cast

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp_refcache import CacheResponse, PreviewConfig, RefCache

P = ParamSpec("P")
T = TypeVar("T")

# Type alias for the Langfuse client (helps with type narrowing)
_LangfuseClient = Any  # Will be Langfuse when available

# =============================================================================
# Langfuse Initialization
# =============================================================================

# Try to import Langfuse - gracefully degrade if not available
_langfuse_available: bool = False
_langfuse_client: _LangfuseClient = None
_observe_func: Any = None
_propagate_attributes_func: Any = None

try:
    from langfuse import get_client as _get_client
    from langfuse import (
        observe as _observe,  # pyright: ignore[reportUnknownVariableType]
    )
    from langfuse import propagate_attributes as _propagate

    _langfuse_available = True
    _langfuse_client = _get_client()
    _observe_func = _observe  # pyright: ignore[reportUnknownVariableType]
    _propagate_attributes_func = _propagate
except ImportError:
    pass

# Public aliases (for backward compatibility)
langfuse = _langfuse_client
observe = _observe_func
propagate_attributes = _propagate_attributes_func

# Check if Langfuse is properly configured
_langfuse_enabled: bool = _langfuse_available and all(
    [
        os.getenv("LANGFUSE_PUBLIC_KEY"),
        os.getenv("LANGFUSE_SECRET_KEY"),
    ]
)

if _langfuse_available and not _langfuse_enabled:
    import sys

    print(
        "Warning: Langfuse credentials not set. Tracing will be disabled.\n"
        "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable tracing.",
        file=sys.stderr,
    )


def is_langfuse_enabled() -> bool:
    """Check if Langfuse tracing is enabled."""
    return _langfuse_enabled


def _get_langfuse() -> Any:
    """Get the Langfuse client (for internal use with type safety)."""
    return _langfuse_client


def _get_propagate_attributes() -> Any:
    """Get the propagate_attributes context manager."""
    return _propagate_attributes_func


# =============================================================================
# Mock Context for Testing
# =============================================================================


class MockContext:
    """Mock FastMCP Context for testing context-scoped caching with Langfuse.

    This class simulates a FastMCP Context object with the minimum API
    needed for context-scoped caching and Langfuse attribution:
    - session_id attribute
    - get_state(key) method for retrieving identity values
    """

    # Class-level state storage (shared across all instances)
    _state: ClassVar[dict[str, str]] = {
        "user_id": "demo_user",
        "org_id": "demo_org",
        "agent_id": "demo_agent",
    }
    _session_id: ClassVar[str] = "demo_session_001"

    @property
    def session_id(self) -> str:
        """Get the current session ID."""
        return MockContext._session_id

    @property
    def client_id(self) -> str:
        """Get the client ID (for compatibility)."""
        return "demo_client"

    @property
    def request_id(self) -> str:
        """Get the request ID (for compatibility)."""
        return "demo_request"

    def get_state(self, key: str) -> str | None:
        """Get a state value by key."""
        return MockContext._state.get(key)

    @classmethod
    def set_state(cls, **kwargs: str) -> None:
        """Update state values."""
        cls._state.update(kwargs)

    @classmethod
    def set_session_id(cls, session_id: str) -> None:
        """Update the session ID."""
        cls._session_id = session_id

    @classmethod
    def get_current_state(cls) -> dict[str, Any]:
        """Get a copy of current state for inspection."""
        return {
            **cls._state,
            "session_id": cls._session_id,
        }

    @classmethod
    def reset(cls) -> None:
        """Reset to default test values."""
        cls._state = {
            "user_id": "demo_user",
            "org_id": "demo_org",
            "agent_id": "demo_agent",
        }
        cls._session_id = "demo_session_001"


# =============================================================================
# Context Integration
# =============================================================================

# Store original function for restoration
_test_mode_enabled = False

# Try to import context integration
_has_context_integration: bool = False
_original_try_get_context: Any = None
_ctx_integration_module: Any = None

try:
    import mcp_refcache.context_integration as _ctx_mod

    _ctx_integration_module = _ctx_mod
    _original_try_get_context = _ctx_mod.try_get_fastmcp_context
    _has_context_integration = True
except (ImportError, AttributeError):
    pass


def _mock_try_get_fastmcp_context() -> MockContext | None:
    """Mock version that returns our test context."""
    if _test_mode_enabled:
        return MockContext()
    if _original_try_get_context is not None:
        result: MockContext | None = _original_try_get_context()
        return result
    return None


# Patch the context integration module if available
if _has_context_integration and _ctx_integration_module is not None:
    _ctx_integration_module.try_get_fastmcp_context = _mock_try_get_fastmcp_context


def enable_test_mode(enabled: bool = True) -> None:
    """Enable or disable test context mode."""
    global _test_mode_enabled
    _test_mode_enabled = enabled


def is_test_mode_enabled() -> bool:
    """Check if test mode is enabled."""
    return _test_mode_enabled


# =============================================================================
# Langfuse Attribute Extraction
# =============================================================================


def get_langfuse_attributes(
    context: MockContext | None = None,
    cache_namespace: str | None = None,
    operation: str | None = None,
) -> dict[str, Any]:
    """Extract Langfuse-compatible attributes from context.

    This function extracts user_id, session_id, and metadata from the
    current context (MockContext or FastMCP) for use with propagate_attributes().

    Langfuse SDK v3 requirements:
    - Values must be strings ≤200 characters
    - Metadata keys: alphanumeric only (no whitespace or special characters)
    - user_id and session_id are native Langfuse fields

    Args:
        context: Optional context object. If None, attempts to get from test mode.
        cache_namespace: Optional cache namespace to include in metadata.
        operation: Optional operation name (e.g., "cache_set", "cache_get").

    Returns:
        Dict with keys: user_id, session_id, metadata, tags, version
        All values are Langfuse-compatible (strings, alphanumeric keys).
    """
    # Try to get context if not provided
    if context is None:
        context = _mock_try_get_fastmcp_context()

    # Default values when no context available
    user_id = "anonymous"
    session_id = "nosession"
    org_id = "default"
    agent_id = "unknown"

    # Extract from context if available
    if context is not None:
        user_id = context.get_state("user_id") or user_id
        session_id = getattr(context, "session_id", None) or session_id
        org_id = context.get_state("org_id") or org_id
        agent_id = context.get_state("agent_id") or agent_id

    # Truncate to ≤200 chars (Langfuse requirement)
    user_id = str(user_id)[:200]
    session_id = str(session_id)[:200]

    # Build metadata dict (alphanumeric keys only)
    metadata: dict[str, str] = {
        "orgid": str(org_id)[:200],
        "agentid": str(agent_id)[:200],
        "server": "fastmcptemplate",
    }

    # Add optional fields
    if cache_namespace:
        metadata["cachenamespace"] = str(cache_namespace)[:200]
    if operation:
        metadata["operation"] = str(operation)[:200]

    # Build tags for filtering
    tags = ["fastmcptemplate", "mcprefcache"]
    if operation:
        tags.append(operation.replace("_", ""))
    if _test_mode_enabled:
        tags.append("testmode")

    return {
        "user_id": user_id,
        "session_id": session_id,
        "metadata": metadata,
        "tags": tags,
        "version": "1.0.0",
    }


# =============================================================================
# TracedRefCache Wrapper
# =============================================================================


class TracedRefCache:
    """RefCache wrapper that adds Langfuse tracing with context propagation.

    This wrapper intercepts cache operations and creates Langfuse spans
    for observability. Each operation is traced with:
    - user_id and session_id (native Langfuse fields for aggregation)
    - Full context metadata (org_id, agent_id, cache_namespace)
    - Cache hit/miss status and timing information

    Uses propagate_attributes() to ensure all child spans inherit context.

    Example:
        ```python
        from mcp_refcache import RefCache
        from app.tracing import TracedRefCache

        _cache = RefCache(name="my-cache")
        cache = TracedRefCache(_cache)

        # All cache operations are now traced
        ref = cache.set("key", "value")
        ```
    """

    def __init__(self, cache: RefCache) -> None:
        """Initialize the traced cache wrapper.

        Args:
            cache: The underlying RefCache instance to wrap.
        """
        self._cache = cache

    @property
    def name(self) -> str:
        """Get the cache name."""
        name: str = self._cache.name
        return name

    @property
    def preview_config(self) -> PreviewConfig:
        """Expose preview config from underlying cache."""
        return self._cache.preview_config

    def set(
        self,
        key: str,
        value: Any,
        namespace: str = "public",
        **kwargs: Any,
    ) -> Any:
        """Set a value in cache with Langfuse tracing and context propagation.

        Creates a span for the cache set operation with:
        - user_id, session_id propagated to all child spans
        - Full context metadata (org_id, agent_id, namespace)
        - Operation result and ref_id
        """
        if not _langfuse_enabled or _langfuse_client is None:
            return self._cache.set(key, value, namespace=namespace, **kwargs)

        # Get Langfuse attributes from current context
        attributes = get_langfuse_attributes(
            cache_namespace=namespace,
            operation="cache_set",
        )

        client = _get_langfuse()
        prop_attrs = _get_propagate_attributes()

        with (
            client.start_as_current_observation(
                as_type="span",
                name="cache.set",
                input={"key": key, "namespace": namespace},
            ) as span,
            prop_attrs(
                user_id=attributes["user_id"],
                session_id=attributes["session_id"],
                metadata=attributes["metadata"],
                tags=attributes["tags"],
                version=attributes["version"],
            ),
        ):
            try:
                result = self._cache.set(key, value, namespace=namespace, **kwargs)
                span.update(
                    output={
                        "ref_id": result.ref_id
                        if hasattr(result, "ref_id")
                        else str(result),
                        "success": True,
                    },
                    metadata={
                        "cacheoperation": "set",
                        "namespace": namespace,
                        "userid": attributes["user_id"],
                        "sessionid": attributes["session_id"],
                    },
                )
                client.flush()
                return result
            except Exception as e:
                span.update(
                    output={"error": str(e), "success": False},
                    metadata={
                        "cacheoperation": "set",
                        "errortype": type(e).__name__,
                    },
                )
                client.flush()
                raise

    def get(
        self,
        ref_id: str,
        actor: Any = None,
        **kwargs: Any,
    ) -> CacheResponse:
        """Get a value from cache with Langfuse tracing and context propagation.

        Creates a span for the cache get operation with:
        - user_id, session_id propagated to all child spans
        - Cache hit/miss status
        - Pagination and preview information
        """
        if not _langfuse_enabled or _langfuse_client is None:
            return self._cache.get(ref_id, actor=actor, **kwargs)

        # Get Langfuse attributes from current context
        attributes = get_langfuse_attributes(
            operation="cache_get",
        )

        client = _get_langfuse()
        prop_attrs = _get_propagate_attributes()

        with (
            client.start_as_current_observation(
                as_type="span",
                name="cache.get",
                input={"ref_id": ref_id},
            ) as span,
            prop_attrs(
                user_id=attributes["user_id"],
                session_id=attributes["session_id"],
                metadata=attributes["metadata"],
                tags=attributes["tags"],
                version=attributes["version"],
            ),
        ):
            try:
                result = self._cache.get(ref_id, actor=actor, **kwargs)
                is_hit = result.preview is not None

                span.update(
                    output={
                        "cache_hit": is_hit,
                        "is_complete": getattr(result, "is_complete", None),
                    },
                    metadata={
                        "cacheoperation": "get",
                        "cachehit": str(is_hit).lower(),
                        "refid": ref_id,
                        "userid": attributes["user_id"],
                        "sessionid": attributes["session_id"],
                    },
                )
                client.flush()
                return result
            except Exception as e:
                span.update(
                    output={"error": str(e), "cache_hit": False},
                    metadata={
                        "cacheoperation": "get",
                        "errortype": type(e).__name__,
                    },
                )
                client.flush()
                raise

    def resolve(self, ref_id: str, actor: Any = None) -> Any:
        """Resolve a ref_id to its value with Langfuse tracing.

        Creates a span for ref_id resolution with context propagation.
        """
        if not _langfuse_enabled or _langfuse_client is None:
            return self._cache.resolve(ref_id, actor=actor)

        # Get Langfuse attributes from current context
        attributes = get_langfuse_attributes(
            operation="cache_resolve",
        )

        client = _get_langfuse()
        prop_attrs = _get_propagate_attributes()

        with (
            client.start_as_current_observation(
                as_type="span",
                name="cache.resolve",
                input={"ref_id": ref_id},
            ) as span,
            prop_attrs(
                user_id=attributes["user_id"],
                session_id=attributes["session_id"],
                metadata=attributes["metadata"],
                tags=attributes["tags"],
                version=attributes["version"],
            ),
        ):
            try:
                result = self._cache.resolve(ref_id, actor=actor)
                span.update(
                    output={
                        "resolved": result is not None,
                        "value_type": type(result).__name__ if result else None,
                    },
                    metadata={
                        "cacheoperation": "resolve",
                        "refid": ref_id,
                        "userid": attributes["user_id"],
                        "sessionid": attributes["session_id"],
                    },
                )
                client.flush()
                return result
            except Exception as e:
                span.update(
                    output={"error": str(e), "resolved": False},
                    metadata={
                        "cacheoperation": "resolve",
                        "errortype": type(e).__name__,
                    },
                )
                client.flush()
                raise

    def cached(
        self,
        namespace: str = "public",
        **decorator_kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., dict[str, Any]]]:
        """Decorator that caches function results with Langfuse tracing.

        This enhanced decorator wraps the underlying @cache.cached() decorator
        and adds Langfuse spans for cache operations. Each cache operation
        is traced with:
        - user_id and session_id for attribution
        - Cache hit/miss status
        - Namespace and operation metadata

        Args:
            namespace: Cache namespace (supports context templates like "user:{user_id}")
            **decorator_kwargs: Additional arguments passed to underlying cached()

        Returns:
            Decorated function that returns structured cache responses with tracing.

        Example:
            ```python
            @cache.cached(namespace="public")
            async def generate_items(count: int) -> list:
                return [{"id": i} for i in range(count)]
            ```
        """
        # Get the underlying decorator
        underlying_decorator = self._cache.cached(
            namespace=namespace, **decorator_kwargs
        )

        def tracing_decorator(
            func: Callable[..., Any],
        ) -> Callable[..., Any]:
            """Wrap function with Langfuse tracing for cache operations."""
            # Apply underlying decorator first
            cached_func = underlying_decorator(func)

            if asyncio.iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_traced_wrapper(
                    *args: Any, **kwargs: Any
                ) -> dict[str, Any]:
                    if not _langfuse_enabled or _langfuse_client is None:
                        result = await cached_func(*args, **kwargs)
                        return cast("dict[str, Any]", result)

                    # Get Langfuse attributes from context
                    attributes = get_langfuse_attributes(
                        cache_namespace=namespace,
                        operation="cached_call",
                    )

                    client = _get_langfuse()
                    prop_attrs = _get_propagate_attributes()

                    with (
                        client.start_as_current_observation(
                            as_type="span",
                            name=f"cache.{func.__name__}",
                            input={
                                "function": func.__name__,
                                "namespace": namespace,
                                "args_count": len(args),
                            },
                        ) as span,
                        prop_attrs(
                            user_id=attributes["user_id"],
                            session_id=attributes["session_id"],
                            metadata=attributes["metadata"],
                            tags=attributes["tags"],
                            version=attributes["version"],
                        ),
                    ):
                        try:
                            result = await cached_func(*args, **kwargs)
                            result_dict = cast("dict[str, Any]", result)

                            # Determine if this was a cache hit
                            is_cached = "ref_id" in result_dict

                            span.update(
                                output={
                                    "ref_id": result_dict.get("ref_id"),
                                    "is_complete": result_dict.get("is_complete"),
                                    "cached": is_cached,
                                },
                                metadata={
                                    "cacheoperation": "cached_call",
                                    "function": func.__name__,
                                    "namespace": namespace,
                                    "userid": attributes["user_id"],
                                    "sessionid": attributes["session_id"],
                                },
                            )
                            client.flush()
                            return result_dict
                        except Exception as e:
                            span.update(
                                output={"error": str(e), "cached": False},
                                metadata={
                                    "cacheoperation": "cached_call",
                                    "errortype": type(e).__name__,
                                },
                            )
                            client.flush()
                            raise

                return async_traced_wrapper
            else:

                @functools.wraps(func)
                def sync_traced_wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
                    if not _langfuse_enabled or _langfuse_client is None:
                        result = cached_func(*args, **kwargs)
                        return cast("dict[str, Any]", result)

                    # Get Langfuse attributes from context
                    attributes = get_langfuse_attributes(
                        cache_namespace=namespace,
                        operation="cached_call",
                    )

                    client = _get_langfuse()
                    prop_attrs = _get_propagate_attributes()

                    with (
                        client.start_as_current_observation(
                            as_type="span",
                            name=f"cache.{func.__name__}",
                            input={
                                "function": func.__name__,
                                "namespace": namespace,
                                "args_count": len(args),
                            },
                        ) as span,
                        prop_attrs(
                            user_id=attributes["user_id"],
                            session_id=attributes["session_id"],
                            metadata=attributes["metadata"],
                            tags=attributes["tags"],
                            version=attributes["version"],
                        ),
                    ):
                        try:
                            result = cached_func(*args, **kwargs)
                            result_dict = cast("dict[str, Any]", result)

                            # Determine if this was a cache hit
                            is_cached = "ref_id" in result_dict

                            span.update(
                                output={
                                    "ref_id": result_dict.get("ref_id"),
                                    "is_complete": result_dict.get("is_complete"),
                                    "cached": is_cached,
                                },
                                metadata={
                                    "cacheoperation": "cached_call",
                                    "function": func.__name__,
                                    "namespace": namespace,
                                    "userid": attributes["user_id"],
                                    "sessionid": attributes["session_id"],
                                },
                            )
                            client.flush()
                            return result_dict
                        except Exception as e:
                            span.update(
                                output={"error": str(e), "cached": False},
                                metadata={
                                    "cacheoperation": "cached_call",
                                    "errortype": type(e).__name__,
                                },
                            )
                            client.flush()
                            raise

                return sync_traced_wrapper

        return tracing_decorator

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to underlying cache."""
        return getattr(self._cache, name)


# =============================================================================
# Traced Tool Decorator
# =============================================================================


def traced_tool(
    name: str | None = None,
    capture_input: bool = True,
    capture_output: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that adds Langfuse tracing to a function.

    This decorator wraps a function with Langfuse's @observe decorator
    and automatically propagates context attributes.

    Args:
        name: Optional name for the trace span (defaults to function name).
        capture_input: Whether to capture function inputs in trace.
        capture_output: Whether to capture function outputs in trace.

    Returns:
        Decorated function with Langfuse tracing.

    Example:
        ```python
        @traced_tool("my_operation")
        def my_function(arg: str) -> dict:
            return {"result": arg}
        ```
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not _langfuse_enabled or _observe_func is None or _langfuse_client is None:
            return func

        # Apply Langfuse observe decorator
        observed = _observe_func(
            name=name or func.__name__,
            capture_input=capture_input,
            capture_output=capture_output,
        )(func)

        client = _get_langfuse()
        prop_attrs = _get_propagate_attributes()

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                attributes = get_langfuse_attributes(operation=name or func.__name__)
                with prop_attrs(
                    user_id=attributes["user_id"],
                    session_id=attributes["session_id"],
                    metadata=attributes["metadata"],
                    tags=attributes["tags"],
                    version=attributes["version"],
                ):
                    result = await observed(*args, **kwargs)
                    client.flush()
                    return result

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                attributes = get_langfuse_attributes(operation=name or func.__name__)
                with prop_attrs(
                    user_id=attributes["user_id"],
                    session_id=attributes["session_id"],
                    metadata=attributes["metadata"],
                    tags=attributes["tags"],
                    version=attributes["version"],
                ):
                    result = observed(*args, **kwargs)
                    client.flush()
                    return result

            return sync_wrapper

    return decorator


# =============================================================================
# Cleanup
# =============================================================================


def flush_traces() -> None:
    """Flush all pending traces to Langfuse."""
    if _langfuse_enabled and _langfuse_client is not None:
        _langfuse_client.flush()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "MockContext",
    "TracedRefCache",
    "enable_test_mode",
    "flush_traces",
    "get_langfuse_attributes",
    "is_langfuse_enabled",
    "is_test_mode_enabled",
    "langfuse",
    "observe",
    "propagate_attributes",
    "traced_tool",
]
