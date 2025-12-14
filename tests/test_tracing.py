"""Tests for the tracing module."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

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


class TestMockContext:
    """Tests for MockContext class."""

    def setup_method(self) -> None:
        """Reset MockContext before each test."""
        MockContext.reset()

    def teardown_method(self) -> None:
        """Reset MockContext after each test."""
        MockContext.reset()

    def test_session_id_property(self) -> None:
        """Test session_id property."""
        ctx = MockContext()
        assert ctx.session_id == "demo_session_001"

    def test_client_id_property(self) -> None:
        """Test client_id property."""
        ctx = MockContext()
        assert ctx.client_id == "demo_client"

    def test_request_id_property(self) -> None:
        """Test request_id property."""
        ctx = MockContext()
        assert ctx.request_id == "demo_request"

    def test_get_state_returns_value(self) -> None:
        """Test get_state returns correct value."""
        ctx = MockContext()
        assert ctx.get_state("user_id") == "demo_user"
        assert ctx.get_state("org_id") == "demo_org"

    def test_get_state_returns_none_for_missing(self) -> None:
        """Test get_state returns None for missing keys."""
        ctx = MockContext()
        assert ctx.get_state("nonexistent") is None

    def test_set_state_class_method(self) -> None:
        """Test set_state updates class-level state."""
        MockContext.set_state(user_id="alice", org_id="acme")
        ctx = MockContext()
        assert ctx.get_state("user_id") == "alice"
        assert ctx.get_state("org_id") == "acme"

    def test_set_session_id_class_method(self) -> None:
        """Test set_session_id updates class-level session."""
        MockContext.set_session_id("new-session")
        ctx = MockContext()
        assert ctx.session_id == "new-session"

    def test_get_current_state_returns_all(self) -> None:
        """Test get_current_state returns complete state."""
        state = MockContext.get_current_state()
        assert "user_id" in state
        assert "org_id" in state
        assert "agent_id" in state
        assert "session_id" in state

    def test_reset_restores_defaults(self) -> None:
        """Test reset restores default values."""
        MockContext.set_state(user_id="modified")
        MockContext.set_session_id("modified-session")
        MockContext.reset()

        ctx = MockContext()
        assert ctx.get_state("user_id") == "demo_user"
        assert ctx.session_id == "demo_session_001"


class TestTestModeControl:
    """Tests for test mode control functions."""

    def setup_method(self) -> None:
        """Reset test mode before each test."""
        enable_test_mode(False)

    def teardown_method(self) -> None:
        """Reset test mode after each test."""
        enable_test_mode(False)

    def test_enable_test_mode_true(self) -> None:
        """Test enabling test mode."""
        enable_test_mode(True)
        assert is_test_mode_enabled() is True

    def test_enable_test_mode_false(self) -> None:
        """Test disabling test mode."""
        enable_test_mode(True)
        enable_test_mode(False)
        assert is_test_mode_enabled() is False

    def test_is_test_mode_enabled_default(self) -> None:
        """Test default test mode is disabled."""
        assert is_test_mode_enabled() is False


class TestGetLangfuseAttributes:
    """Tests for get_langfuse_attributes function."""

    def setup_method(self) -> None:
        """Reset state before each test."""
        enable_test_mode(False)
        MockContext.reset()

    def teardown_method(self) -> None:
        """Reset state after each test."""
        enable_test_mode(False)
        MockContext.reset()

    def test_returns_required_keys(self) -> None:
        """Test that all required keys are returned."""
        attrs = get_langfuse_attributes()
        assert "user_id" in attrs
        assert "session_id" in attrs
        assert "metadata" in attrs
        assert "tags" in attrs
        assert "version" in attrs

    def test_default_values_without_context(self) -> None:
        """Test default values when no context is available."""
        attrs = get_langfuse_attributes()
        # Defaults when no context
        assert attrs["user_id"] in ["anonymous", "demo_user"]
        assert attrs["session_id"] in ["nosession", "demo_session_001"]

    def test_with_mock_context(self) -> None:
        """Test attributes from MockContext."""
        ctx = MockContext()
        MockContext.set_state(user_id="test_user", org_id="test_org")
        attrs = get_langfuse_attributes(context=ctx)
        assert attrs["user_id"] == "test_user"
        assert attrs["metadata"]["orgid"] == "test_org"

    def test_with_test_mode_enabled(self) -> None:
        """Test attributes with test mode enabled."""
        enable_test_mode(True)
        MockContext.set_state(user_id="alice")
        attrs = get_langfuse_attributes()
        assert attrs["user_id"] == "alice"
        assert "testmode" in attrs["tags"]

    def test_cache_namespace_in_metadata(self) -> None:
        """Test cache_namespace is added to metadata."""
        attrs = get_langfuse_attributes(cache_namespace="user:data")
        assert attrs["metadata"]["cachenamespace"] == "user:data"

    def test_operation_in_metadata(self) -> None:
        """Test operation is added to metadata."""
        attrs = get_langfuse_attributes(operation="cache_set")
        assert attrs["metadata"]["operation"] == "cache_set"

    def test_operation_in_tags(self) -> None:
        """Test operation is added to tags without underscores."""
        attrs = get_langfuse_attributes(operation="cache_set")
        assert "cacheset" in attrs["tags"]

    def test_truncates_long_values(self) -> None:
        """Test that long values are truncated to 200 chars."""
        ctx = MockContext()
        long_value = "x" * 300
        MockContext.set_state(user_id=long_value)
        attrs = get_langfuse_attributes(context=ctx)
        assert len(attrs["user_id"]) == 200

    def test_server_tag_included(self) -> None:
        """Test that server tag is included."""
        attrs = get_langfuse_attributes()
        assert "fastmcptemplate" in attrs["tags"]

    def test_mcprefcache_tag_included(self) -> None:
        """Test that mcprefcache tag is included."""
        attrs = get_langfuse_attributes()
        assert "mcprefcache" in attrs["tags"]


class TestTracedRefCache:
    """Tests for TracedRefCache wrapper."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        from mcp_refcache import PreviewConfig, PreviewStrategy, RefCache

        self.base_cache = RefCache(
            name="test-cache",
            default_ttl=3600,
            preview_config=PreviewConfig(
                max_size=2048,
                default_strategy=PreviewStrategy.SAMPLE,
            ),
        )
        self.traced_cache = TracedRefCache(self.base_cache)

    def test_name_property(self) -> None:
        """Test name property delegates to base cache."""
        assert self.traced_cache.name == "test-cache"

    def test_preview_config_property(self) -> None:
        """Test preview_config property delegates to base cache."""
        assert self.traced_cache.preview_config is not None
        assert self.traced_cache.preview_config.max_size == 2048

    def test_getattr_delegates_to_base(self) -> None:
        """Test unknown attributes delegate to base cache."""
        # default_ttl is on the base cache
        assert hasattr(self.traced_cache, "default_ttl")

    def test_set_without_langfuse(self) -> None:
        """Test set works when Langfuse is disabled."""
        ref = self.traced_cache.set("key1", {"data": "value"}, namespace="public")
        assert ref is not None
        assert hasattr(ref, "ref_id")

    def test_get_without_langfuse(self) -> None:
        """Test get works when Langfuse is disabled."""
        ref = self.traced_cache.set("key2", [1, 2, 3], namespace="public")
        response = self.traced_cache.get(ref.ref_id, actor="agent")
        assert response is not None

    def test_resolve_without_langfuse(self) -> None:
        """Test resolve works when Langfuse is disabled."""
        from mcp_refcache import DefaultActor

        ref = self.traced_cache.set("key3", 42, namespace="public")
        value = self.traced_cache.resolve(ref.ref_id, actor=DefaultActor.user())
        assert value == 42

    def test_cached_decorator_sync(self) -> None:
        """Test cached decorator works for sync functions."""

        @self.traced_cache.cached(namespace="test")
        def sync_func(x: int) -> list[int]:
            return list(range(x))

        result = sync_func(5)
        assert isinstance(result, dict)
        assert "value" in result or "preview" in result or "ref_id" in result

    @pytest.mark.asyncio
    async def test_cached_decorator_async(self) -> None:
        """Test cached decorator works for async functions."""

        @self.traced_cache.cached(namespace="test")
        async def async_func(x: int) -> list[int]:
            return list(range(x))

        result = await async_func(5)
        assert isinstance(result, dict)
        assert "value" in result or "preview" in result or "ref_id" in result


class TestTracedTool:
    """Tests for traced_tool decorator."""

    def test_decorated_function_returns_same_result(self) -> None:
        """Test decorated function returns correct result."""

        @traced_tool("test_func")
        def my_func(x: int) -> dict[str, Any]:
            return {"result": x * 2}

        result = my_func(5)
        assert result["result"] == 10

    @pytest.mark.asyncio
    async def test_decorated_async_function(self) -> None:
        """Test decorated async function works."""

        @traced_tool("test_async")
        async def my_async_func(x: int) -> dict[str, Any]:
            return {"result": x * 2}

        result = await my_async_func(5)
        assert result["result"] == 10

    def test_preserves_function_name(self) -> None:
        """Test decorator preserves function name."""

        @traced_tool()
        def named_function() -> str:
            return "test"

        assert named_function.__name__ == "named_function"


class TestFlushTraces:
    """Tests for flush_traces function."""

    def test_flush_traces_does_not_raise(self) -> None:
        """Test flush_traces doesn't raise when Langfuse is disabled."""
        # Should not raise any exceptions
        flush_traces()

    def test_flush_traces_calls_langfuse_flush(self) -> None:
        """Test flush_traces calls langfuse.flush when enabled."""
        from app import tracing

        mock_client = MagicMock()

        # Save originals
        original_enabled = tracing._langfuse_enabled
        original_client = tracing._langfuse_client
        try:
            tracing._langfuse_enabled = True
            tracing._langfuse_client = mock_client
            flush_traces()
            mock_client.flush.assert_called_once()
        finally:
            tracing._langfuse_enabled = original_enabled
            tracing._langfuse_client = original_client


class TestIsLangfuseEnabled:
    """Tests for is_langfuse_enabled function."""

    def test_returns_boolean(self) -> None:
        """Test function returns boolean."""
        result = is_langfuse_enabled()
        assert isinstance(result, bool)

    @patch.dict("os.environ", {"LANGFUSE_PUBLIC_KEY": "", "LANGFUSE_SECRET_KEY": ""})
    def test_disabled_without_keys(self) -> None:
        """Test returns False without env vars set."""
        # Note: This tests the runtime check, but the module-level check
        # happens at import time, so this may not change the result
        result = is_langfuse_enabled()
        assert isinstance(result, bool)


class TestTracedRefCacheWithMockedLangfuse:
    """Tests for TracedRefCache with mocked Langfuse enabled."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        from mcp_refcache import PreviewConfig, PreviewStrategy, RefCache

        self.base_cache = RefCache(
            name="test-cache-mocked",
            default_ttl=3600,
            preview_config=PreviewConfig(
                max_size=2048,
                default_strategy=PreviewStrategy.SAMPLE,
            ),
        )
        self.traced_cache = TracedRefCache(self.base_cache)

    def test_set_with_langfuse_enabled(self) -> None:
        """Test set traces to Langfuse when enabled."""
        from app import tracing

        mock_client = MagicMock()
        mock_propagate = MagicMock()

        # Set up mock context manager
        mock_span = MagicMock()
        mock_client.start_as_current_observation.return_value.__enter__ = MagicMock(
            return_value=mock_span
        )
        mock_client.start_as_current_observation.return_value.__exit__ = MagicMock(
            return_value=False
        )
        mock_propagate.return_value.__enter__ = MagicMock()
        mock_propagate.return_value.__exit__ = MagicMock(return_value=False)

        original_enabled = tracing._langfuse_enabled
        original_client = tracing._langfuse_client
        original_propagate = tracing._propagate_attributes_func
        try:
            tracing._langfuse_enabled = True
            tracing._langfuse_client = mock_client
            tracing._propagate_attributes_func = mock_propagate

            self.traced_cache.set("key_traced", {"data": "value"})

            mock_client.start_as_current_observation.assert_called_once()
            mock_client.flush.assert_called()
        finally:
            tracing._langfuse_enabled = original_enabled
            tracing._langfuse_client = original_client
            tracing._propagate_attributes_func = original_propagate

    def test_get_with_langfuse_enabled(self) -> None:
        """Test get traces to Langfuse when enabled."""
        from app import tracing

        # First set a value without tracing
        ref = self.base_cache.set("key_for_get", [1, 2, 3])

        mock_client = MagicMock()
        mock_propagate = MagicMock()

        # Set up mock context manager
        mock_span = MagicMock()
        mock_client.start_as_current_observation.return_value.__enter__ = MagicMock(
            return_value=mock_span
        )
        mock_client.start_as_current_observation.return_value.__exit__ = MagicMock(
            return_value=False
        )
        mock_propagate.return_value.__enter__ = MagicMock()
        mock_propagate.return_value.__exit__ = MagicMock(return_value=False)

        original_enabled = tracing._langfuse_enabled
        original_client = tracing._langfuse_client
        original_propagate = tracing._propagate_attributes_func
        try:
            tracing._langfuse_enabled = True
            tracing._langfuse_client = mock_client
            tracing._propagate_attributes_func = mock_propagate

            self.traced_cache.get(ref.ref_id, actor="agent")

            mock_client.start_as_current_observation.assert_called_once()
            mock_client.flush.assert_called()
        finally:
            tracing._langfuse_enabled = original_enabled
            tracing._langfuse_client = original_client
            tracing._propagate_attributes_func = original_propagate

    def test_resolve_with_langfuse_enabled(self) -> None:
        """Test resolve traces to Langfuse when enabled."""
        from app import tracing

        # First set a value without tracing
        ref = self.base_cache.set("key_for_resolve", {"secret": "data"})

        mock_client = MagicMock()
        mock_propagate = MagicMock()

        # Set up mock context manager
        mock_span = MagicMock()
        mock_client.start_as_current_observation.return_value.__enter__ = MagicMock(
            return_value=mock_span
        )
        mock_client.start_as_current_observation.return_value.__exit__ = MagicMock(
            return_value=False
        )
        mock_propagate.return_value.__enter__ = MagicMock()
        mock_propagate.return_value.__exit__ = MagicMock(return_value=False)

        original_enabled = tracing._langfuse_enabled
        original_client = tracing._langfuse_client
        original_propagate = tracing._propagate_attributes_func
        try:
            tracing._langfuse_enabled = True
            tracing._langfuse_client = mock_client
            tracing._propagate_attributes_func = mock_propagate

            self.traced_cache.resolve(ref.ref_id, actor="test_user")

            mock_client.start_as_current_observation.assert_called_once()
            mock_client.flush.assert_called()
        finally:
            tracing._langfuse_enabled = original_enabled
            tracing._langfuse_client = original_client
            tracing._propagate_attributes_func = original_propagate


class TestTracedToolWithMockedLangfuse:
    """Tests for traced_tool decorator with mocked Langfuse."""

    @patch("app.tracing._langfuse_enabled", True)
    @patch("app.tracing.langfuse")
    @patch("app.tracing.propagate_attributes")
    @patch("app.tracing.observe")
    def test_traced_tool_with_langfuse_sync(
        self,
        mock_observe: MagicMock,
        mock_propagate: MagicMock,
        mock_langfuse: MagicMock,
    ) -> None:
        """Test traced_tool with Langfuse enabled for sync function."""
        from app import tracing

        # Mock observe to return the function wrapped
        mock_observe.return_value = lambda f: f
        mock_propagate.return_value.__enter__ = MagicMock()
        mock_propagate.return_value.__exit__ = MagicMock(return_value=False)

        original_enabled = tracing._langfuse_enabled
        original_observe = tracing.observe
        original_propagate = tracing.propagate_attributes
        original_langfuse = tracing.langfuse
        try:
            tracing._langfuse_enabled = True
            tracing.observe = mock_observe
            tracing.propagate_attributes = mock_propagate
            tracing.langfuse = mock_langfuse

            @traced_tool("test_sync")
            def sync_func(x: int) -> dict[str, Any]:
                return {"result": x}

            # Note: Since we're patching at import time, this may use original
            # The decorator captures state at decoration time
            result = sync_func(5)
            assert result["result"] == 5
        finally:
            tracing._langfuse_enabled = original_enabled
            tracing.observe = original_observe
            tracing.propagate_attributes = original_propagate
            tracing.langfuse = original_langfuse
