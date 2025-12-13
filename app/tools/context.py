"""Context management tools for Langfuse attribution testing.

This module provides tools to manage test context for demonstrating
and testing Langfuse tracing with user/session attribution.
"""

from __future__ import annotations

from typing import Any

from app.tracing import (
    MockContext,
    enable_test_mode,
    get_langfuse_attributes,
    is_langfuse_enabled,
    is_test_mode_enabled,
)


def enable_test_context(enabled: bool = True) -> dict[str, Any]:
    """Enable or disable test context mode for Langfuse attribution demos.

    When enabled, all traces will include user_id, session_id, and metadata
    from the MockContext. This allows testing Langfuse filtering and
    aggregation without a real FastMCP authentication setup.

    Args:
        enabled: Whether to enable test context mode (default: True).

    Returns:
        Status dict with current test mode state and context values.
    """
    enable_test_mode(enabled)

    if enabled:
        return {
            "test_mode": True,
            "context": MockContext.get_current_state(),
            "langfuse_enabled": is_langfuse_enabled(),
            "message": (
                "Test context mode enabled. "
                "Traces will include user/session from MockContext."
            ),
        }
    return {
        "test_mode": False,
        "context": None,
        "langfuse_enabled": is_langfuse_enabled(),
        "message": "Test context mode disabled. Context will come from real FastMCP.",
    }


def set_test_context(
    user_id: str | None = None,
    org_id: str | None = None,
    session_id: str | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Set test context values for Langfuse attribution demos.

    Changes here affect what user_id, session_id, and metadata are
    sent to Langfuse traces. Use this to test filtering by different
    users or sessions in the Langfuse dashboard.

    Args:
        user_id: User identity (e.g., "alice", "bob").
        org_id: Organization identity (e.g., "acme", "globex").
        session_id: Session identifier for grouping traces.
        agent_id: Agent identity (e.g., "claude", "gpt4").

    Returns:
        Updated context state and example of Langfuse attributes.
    """
    # Auto-enable test mode when setting context
    if not is_test_mode_enabled():
        enable_test_mode(True)

    if user_id is not None:
        MockContext.set_state(user_id=user_id)
    if org_id is not None:
        MockContext.set_state(org_id=org_id)
    if agent_id is not None:
        MockContext.set_state(agent_id=agent_id)
    if session_id is not None:
        MockContext.set_session_id(session_id)

    # Show what Langfuse will receive
    attributes = get_langfuse_attributes()

    return {
        "context": MockContext.get_current_state(),
        "langfuse_attributes": {
            "user_id": attributes["user_id"],
            "session_id": attributes["session_id"],
            "metadata": attributes["metadata"],
            "tags": attributes["tags"],
        },
        "message": (
            "Context updated. Next tool calls will use these Langfuse attributes."
        ),
    }


def reset_test_context() -> dict[str, Any]:
    """Reset test context to default demo values.

    Returns:
        Reset context state.
    """
    MockContext.reset()
    return {
        "context": MockContext.get_current_state(),
        "message": "Context reset to default demo values.",
    }


def get_trace_info() -> dict[str, Any]:
    """Get information about the current Langfuse trace and context.

    Returns metadata about Langfuse tracing status and current
    context values for debugging.

    Returns:
        Dict with Langfuse configuration and current context.
    """
    import os

    attributes = get_langfuse_attributes()

    return {
        "langfuse_enabled": is_langfuse_enabled(),
        "langfuse_host": os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        "public_key_set": bool(os.getenv("LANGFUSE_PUBLIC_KEY")),
        "secret_key_set": bool(os.getenv("LANGFUSE_SECRET_KEY")),
        "test_mode_enabled": is_test_mode_enabled(),
        "current_context": (
            MockContext.get_current_state() if is_test_mode_enabled() else None
        ),
        "langfuse_attributes": {
            "user_id": attributes["user_id"],
            "session_id": attributes["session_id"],
            "metadata": attributes["metadata"],
            "tags": attributes["tags"],
        },
        "message": (
            "Traces are being sent to Langfuse with user/session attribution"
            if is_langfuse_enabled()
            else "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to enable tracing"
        ),
    }


__all__ = [
    "enable_test_context",
    "get_trace_info",
    "reset_test_context",
    "set_test_context",
]
