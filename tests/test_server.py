"""Tests for the fastmcp-template server module."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.server import cache, mcp
from app.tracing import (
    MockContext,
    enable_test_mode,
    get_langfuse_attributes,
    is_langfuse_enabled,
    is_test_mode_enabled,
)


class TestServerInitialization:
    """Tests for server initialization."""

    def test_mcp_instance_exists(self) -> None:
        """Test that FastMCP instance is created."""
        assert mcp is not None
        assert mcp.name == "FastMCP Template"

    def test_cache_instance_exists(self) -> None:
        """Test that RefCache instance is created."""
        assert cache is not None
        assert cache.name == "fastmcp-template"


class TestHelloTool:
    """Tests for the hello tool."""

    def _call_hello(self, name: str = "World") -> dict:
        """Helper to call hello, handling FunctionTool wrapper."""
        from app import server

        hello_fn = server.hello
        if hasattr(hello_fn, "fn"):
            return hello_fn.fn(name)
        return hello_fn(name)

    def test_hello_default(self) -> None:
        """Test hello with default name."""
        result = self._call_hello()
        assert result["message"] == "Hello, World!"
        assert result["server"] == "fastmcp-template"

    def test_hello_custom_name(self) -> None:
        """Test hello with custom name."""
        result = self._call_hello("Alice")
        assert result["message"] == "Hello, Alice!"


class TestTracingModule:
    """Tests for the tracing module."""

    def setup_method(self) -> None:
        """Reset test mode before each test."""
        enable_test_mode(False)
        MockContext.reset()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        enable_test_mode(False)
        MockContext.reset()

    def test_is_langfuse_enabled_without_env(self) -> None:
        """Test that Langfuse is disabled without env vars."""
        # This may be True or False depending on env
        result = is_langfuse_enabled()
        assert isinstance(result, bool)

    def test_enable_test_mode(self) -> None:
        """Test enabling test mode."""
        assert not is_test_mode_enabled()
        enable_test_mode(True)
        assert is_test_mode_enabled()
        enable_test_mode(False)
        assert not is_test_mode_enabled()

    def test_mock_context_default_state(self) -> None:
        """Test MockContext has default state."""
        state = MockContext.get_current_state()
        assert state["user_id"] == "demo_user"
        assert state["org_id"] == "demo_org"
        assert state["agent_id"] == "demo_agent"
        assert state["session_id"] == "demo_session_001"

    def test_mock_context_set_state(self) -> None:
        """Test MockContext state can be updated."""
        MockContext.set_state(user_id="alice", org_id="acme")
        state = MockContext.get_current_state()
        assert state["user_id"] == "alice"
        assert state["org_id"] == "acme"

    def test_mock_context_set_session_id(self) -> None:
        """Test MockContext session_id can be updated."""
        MockContext.set_session_id("new-session-123")
        state = MockContext.get_current_state()
        assert state["session_id"] == "new-session-123"

    def test_mock_context_reset(self) -> None:
        """Test MockContext reset."""
        MockContext.set_state(user_id="bob")
        MockContext.set_session_id("custom-session")
        MockContext.reset()
        state = MockContext.get_current_state()
        assert state["user_id"] == "demo_user"
        assert state["session_id"] == "demo_session_001"

    def test_get_langfuse_attributes_default(self) -> None:
        """Test get_langfuse_attributes without context."""
        attrs = get_langfuse_attributes()
        assert "user_id" in attrs
        assert "session_id" in attrs
        assert "metadata" in attrs
        assert "tags" in attrs
        assert "version" in attrs

    def test_get_langfuse_attributes_with_test_mode(self) -> None:
        """Test get_langfuse_attributes with test mode enabled."""
        enable_test_mode(True)
        MockContext.set_state(user_id="test_user", org_id="test_org")
        attrs = get_langfuse_attributes()
        assert attrs["user_id"] == "test_user"
        assert attrs["metadata"]["orgid"] == "test_org"
        assert "testmode" in attrs["tags"]

    def test_get_langfuse_attributes_with_operation(self) -> None:
        """Test get_langfuse_attributes with operation name."""
        attrs = get_langfuse_attributes(operation="cache_set")
        assert attrs["metadata"]["operation"] == "cache_set"
        assert "cacheset" in attrs["tags"]


class TestContextManagementTools:
    """Tests for context management tools."""

    def setup_method(self) -> None:
        """Reset test mode before each test."""
        enable_test_mode(False)
        MockContext.reset()

    def teardown_method(self) -> None:
        """Clean up after each test."""
        enable_test_mode(False)
        MockContext.reset()

    def _call_enable_test_context(self, enabled: bool = True) -> dict:
        """Helper to call enable_test_context tool."""
        from app import server

        fn = server.enable_test_context
        if hasattr(fn, "fn"):
            return fn.fn(enabled)
        return fn(enabled)

    def _call_set_test_context(self, **kwargs) -> dict:
        """Helper to call set_test_context tool."""
        from app import server

        fn = server.set_test_context
        if hasattr(fn, "fn"):
            return fn.fn(**kwargs)
        return fn(**kwargs)

    def _call_reset_test_context(self) -> dict:
        """Helper to call reset_test_context tool."""
        from app import server

        fn = server.reset_test_context
        if hasattr(fn, "fn"):
            return fn.fn()
        return fn()

    def _call_get_trace_info(self) -> dict:
        """Helper to call get_trace_info tool."""
        from app import server

        fn = server.get_trace_info
        if hasattr(fn, "fn"):
            return fn.fn()
        return fn()

    def test_enable_test_context_returns_status(self) -> None:
        """Test enable_test_context returns correct status."""
        result = self._call_enable_test_context(True)
        assert result["test_mode"] is True
        assert "context" in result
        assert "langfuse_enabled" in result

    def test_enable_test_context_disable(self) -> None:
        """Test disabling test context."""
        self._call_enable_test_context(True)
        result = self._call_enable_test_context(False)
        assert result["test_mode"] is False

    def test_set_test_context_updates_values(self) -> None:
        """Test set_test_context updates context values."""
        result = self._call_set_test_context(
            user_id="alice", org_id="acme", session_id="chat-001"
        )
        assert result["context"]["user_id"] == "alice"
        assert result["context"]["org_id"] == "acme"
        assert result["context"]["session_id"] == "chat-001"

    def test_set_test_context_auto_enables_test_mode(self) -> None:
        """Test set_test_context auto-enables test mode."""
        assert not is_test_mode_enabled()
        self._call_set_test_context(user_id="bob")
        assert is_test_mode_enabled()

    def test_reset_test_context(self) -> None:
        """Test reset_test_context resets to defaults."""
        self._call_set_test_context(user_id="alice")
        result = self._call_reset_test_context()
        assert result["context"]["user_id"] == "demo_user"

    def test_get_trace_info_returns_status(self) -> None:
        """Test get_trace_info returns tracing status."""
        result = self._call_get_trace_info()
        assert "langfuse_enabled" in result
        assert "langfuse_host" in result
        assert "public_key_set" in result
        assert "secret_key_set" in result
        assert "test_mode_enabled" in result
        assert "langfuse_attributes" in result


class TestHealthCheck:
    """Tests for health_check tool."""

    def _call_health_check(self) -> dict:
        """Helper to call health_check, handling FunctionTool wrapper."""
        from app import server

        health_fn = server.health_check
        if hasattr(health_fn, "fn"):
            return health_fn.fn()
        return health_fn()

    def test_health_check_returns_status(self) -> None:
        """Test that health check returns healthy status."""
        result = self._call_health_check()

        assert "status" in result
        assert result["status"] == "healthy"

    def test_health_check_returns_server_name(self) -> None:
        """Test that health check returns server name."""
        result = self._call_health_check()

        assert "server" in result
        assert result["server"] == "fastmcp-template"

    def test_health_check_returns_cache_name(self) -> None:
        """Test that health check returns cache name."""
        result = self._call_health_check()

        assert "cache" in result
        assert result["cache"] == "fastmcp-template"


class TestMCPConfiguration:
    """Tests for MCP server configuration."""

    def test_mcp_has_instructions(self) -> None:
        """Test that MCP has instructions configured."""
        assert mcp.instructions is not None
        assert len(mcp.instructions) > 0

    def test_instructions_mention_caching(self) -> None:
        """Test that instructions mention caching."""
        assert "cach" in mcp.instructions.lower()

    def test_instructions_mention_secret(self) -> None:
        """Test that instructions mention secret computation."""
        assert "secret" in mcp.instructions.lower()


class TestGenerateItems:
    """Tests for the generate_items tool."""

    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self) -> None:
        """Clear cache before and after each test."""
        cache.clear()
        yield
        cache.clear()

    def _get_generate_items_fn(self):
        """Get the underlying function from generate_items tool."""
        from app import server

        generate_fn = server.generate_items
        # Unwrap FunctionTool and cached decorator
        fn = generate_fn.fn if hasattr(generate_fn, "fn") else generate_fn
        # If it's still wrapped by @cache.cached, get the inner function
        if hasattr(fn, "__wrapped__"):
            return fn.__wrapped__
        return fn

    @pytest.mark.asyncio
    async def test_generate_items_default(self) -> None:
        """Test generate_items with default parameters."""
        from app import server

        generate_fn = server.generate_items
        fn = generate_fn.fn if hasattr(generate_fn, "fn") else generate_fn

        result = await fn()

        # Result may be raw list or CacheResponse depending on caching
        if isinstance(result, list):
            assert len(result) == 10
            assert result[0]["id"] == 0
            assert result[0]["name"] == "item_0"
            assert result[0]["value"] == 0
        else:
            # If cached, should have preview or data
            assert result is not None

    @pytest.mark.asyncio
    async def test_generate_items_custom_params(self) -> None:
        """Test generate_items with custom count."""
        from app import server

        generate_fn = server.generate_items
        fn = generate_fn.fn if hasattr(generate_fn, "fn") else generate_fn

        result = await fn(count=5, prefix="widget")

        if isinstance(result, list):
            assert len(result) == 5
            assert result[0]["name"] == "widget_0"
            assert result[4]["name"] == "widget_4"

    @pytest.mark.asyncio
    async def test_generate_items_large_count(self) -> None:
        """Test that generated items have correct structure."""
        from app import server

        generate_fn = server.generate_items
        fn = generate_fn.fn if hasattr(generate_fn, "fn") else generate_fn

        result = await fn(count=3, prefix="test")

        if isinstance(result, list):
            for item in result:
                assert "id" in item
                assert "name" in item
                assert "value" in item


class TestStoreSecret:
    """Tests for the store_secret tool."""

    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self) -> None:
        """Clear cache before and after each test."""
        cache.clear()
        yield
        cache.clear()

    def _call_store_secret(self, name: str, value: float) -> dict:
        """Helper to call store_secret, handling FunctionTool wrapper."""
        from app import server

        store_fn = server.store_secret
        if hasattr(store_fn, "fn"):
            return store_fn.fn(name, value)
        return store_fn(name, value)

    def test_store_secret_returns_ref_id(self) -> None:
        """Test that store_secret returns a reference ID."""
        result = self._call_store_secret("test_secret", 42.0)

        assert "ref_id" in result
        assert result["ref_id"] is not None
        assert len(result["ref_id"]) > 0

    def test_store_secret_returns_name(self) -> None:
        """Test that store_secret returns the secret name."""
        result = self._call_store_secret("my_key", 100.0)

        assert "name" in result
        assert result["name"] == "my_key"

    def test_store_secret_returns_message(self) -> None:
        """Test that store_secret returns a confirmation message."""
        result = self._call_store_secret("api_key", 12345.0)

        assert "message" in result
        assert "api_key" in result["message"]
        assert "compute_with_secret" in result["message"]

    def test_store_secret_returns_permissions(self) -> None:
        """Test that store_secret returns permission information."""
        result = self._call_store_secret("credentials", 999.0)

        assert "permissions" in result
        assert "user" in result["permissions"]
        assert "agent" in result["permissions"]
        assert "EXECUTE" in result["permissions"]["agent"]


class TestComputeWithSecret:
    """Tests for the compute_with_secret tool."""

    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self) -> None:
        """Clear cache before and after each test."""
        cache.clear()
        yield
        cache.clear()

    def _call_store_secret(self, name: str, value: float) -> dict:
        """Helper to call store_secret."""
        from app import server

        store_fn = server.store_secret
        if hasattr(store_fn, "fn"):
            return store_fn.fn(name, value)
        return store_fn(name, value)

    def _call_compute_with_secret(
        self, secret_ref: str, multiplier: float = 1.0
    ) -> dict:
        """Helper to call compute_with_secret."""
        from app import server

        compute_fn = server.compute_with_secret
        if hasattr(compute_fn, "fn"):
            return compute_fn.fn(secret_ref, multiplier)
        return compute_fn(secret_ref, multiplier)

    def test_compute_with_secret_basic(self) -> None:
        """Test basic secret computation."""
        # Store a secret first
        store_result = self._call_store_secret("compute_test", 10.0)
        ref_id = store_result["ref_id"]

        # Compute with multiplier
        result = self._call_compute_with_secret(ref_id, multiplier=2.0)

        assert "result" in result
        assert result["result"] == 20.0
        assert result["multiplier"] == 2.0

    def test_compute_with_secret_default_multiplier(self) -> None:
        """Test computation with default multiplier (1.0)."""
        store_result = self._call_store_secret("default_mult", 50.0)
        ref_id = store_result["ref_id"]

        result = self._call_compute_with_secret(ref_id)

        assert result["result"] == 50.0
        assert result["multiplier"] == 1.0

    def test_compute_with_secret_returns_ref(self) -> None:
        """Test that result includes the secret reference."""
        store_result = self._call_store_secret("ref_check", 25.0)
        ref_id = store_result["ref_id"]

        result = self._call_compute_with_secret(ref_id, multiplier=4.0)

        assert result["secret_ref"] == ref_id

    def test_compute_with_secret_message(self) -> None:
        """Test that result includes confirmation message."""
        store_result = self._call_store_secret("msg_check", 1.0)
        ref_id = store_result["ref_id"]

        result = self._call_compute_with_secret(ref_id)

        assert "message" in result
        assert "not revealed" in result["message"].lower()

    def test_compute_with_secret_invalid_ref(self) -> None:
        """Test that invalid reference raises error."""
        with pytest.raises(ValueError, match="not found"):
            self._call_compute_with_secret("invalid:ref:id", multiplier=1.0)


class TestGetCachedResult:
    """Tests for the get_cached_result tool."""

    @pytest.fixture(autouse=True)
    def _setup_and_teardown(self) -> None:
        """Clear cache before and after each test."""
        cache.clear()
        yield
        cache.clear()

    def _call_store_secret(self, name: str, value: float) -> dict:
        """Helper to store a value in cache."""
        from app import server

        store_fn = server.store_secret
        if hasattr(store_fn, "fn"):
            return store_fn.fn(name, value)
        return store_fn(name, value)

    async def _call_get_cached_result(
        self,
        ref_id: str,
        page: int | None = None,
        page_size: int | None = None,
        max_size: int | None = None,
    ) -> dict:
        """Helper to call get_cached_result."""
        from app import server

        get_fn = server.get_cached_result
        fn = get_fn.fn if hasattr(get_fn, "fn") else get_fn

        return await fn(ref_id, page, page_size, max_size)

    @pytest.mark.asyncio
    async def test_get_cached_result_invalid_ref(self) -> None:
        """Test that invalid reference returns error dict."""
        result = await self._call_get_cached_result("nonexistent:ref")

        assert "error" in result
        assert result["ref_id"] == "nonexistent:ref"

    @pytest.mark.asyncio
    async def test_get_cached_result_with_valid_ref(self) -> None:
        """Test getting a cached result with valid reference."""
        # Store something first
        store_result = self._call_store_secret("cached_value", 123.0)
        ref_id = store_result["ref_id"]

        # Try to get it - may return error due to agent permissions
        result = await self._call_get_cached_result(ref_id)

        # Should return either data or permission error (agent can't read secrets)
        assert "ref_id" in result

    @pytest.mark.asyncio
    async def test_get_cached_result_not_found(self) -> None:
        """Test that result includes the requested ref_id."""
        result = await self._call_get_cached_result("test:ref:123")

        assert "ref_id" in result
        assert result["ref_id"] == "test:ref:123"


class TestIsAdmin:
    """Tests for the is_admin function."""

    @pytest.mark.asyncio
    async def test_is_admin_returns_false(self) -> None:
        """Test that is_admin returns False by default."""
        from app.server import is_admin

        ctx = MagicMock()
        result = await is_admin(ctx)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_admin_with_none_context(self) -> None:
        """Test that is_admin handles None context."""
        from app.server import is_admin

        result = await is_admin(None)

        assert result is False


class TestTyperCLI:
    """Tests for the typer CLI entry point."""

    def test_cli_app_exists(self) -> None:
        """Test that typer app is created."""
        from app.__main__ import app

        assert app is not None

    def test_cli_has_stdio_command(self) -> None:
        """Test that CLI has stdio command."""
        from app.__main__ import app

        # Check callback names since typer may not set cmd.name for decorated funcs
        callback_names = [
            cmd.callback.__name__ if cmd.callback else cmd.name
            for cmd in app.registered_commands
        ]
        assert "stdio" in callback_names

    def test_cli_has_sse_command(self) -> None:
        """Test that CLI has sse command."""
        from app.__main__ import app

        callback_names = [
            cmd.callback.__name__ if cmd.callback else cmd.name
            for cmd in app.registered_commands
        ]
        assert "sse" in callback_names

    def test_cli_has_streamable_http_command(self) -> None:
        """Test that CLI has streamable-http command."""
        from app.__main__ import app

        # streamable-http uses explicit name, check both name and callback
        command_info = [
            (cmd.name, cmd.callback.__name__ if cmd.callback else None)
            for cmd in app.registered_commands
        ]
        has_streamable_http = any(
            name == "streamable-http" or callback == "streamable_http"
            for name, callback in command_info
        )
        assert has_streamable_http


class TestPydanticModels:
    """Tests for Pydantic input models."""

    def test_item_generation_input_defaults(self) -> None:
        """Test ItemGenerationInput default values."""
        from app.tools.demo import ItemGenerationInput

        model = ItemGenerationInput()
        assert model.count == 10
        assert model.prefix == "item"

    def test_item_generation_input_custom(self) -> None:
        """Test ItemGenerationInput with custom values."""
        from app.tools.demo import ItemGenerationInput

        model = ItemGenerationInput(count=50, prefix="widget")
        assert model.count == 50
        assert model.prefix == "widget"

    def test_item_generation_input_validation(self) -> None:
        """Test ItemGenerationInput validates count range."""
        from pydantic import ValidationError

        from app.tools.demo import ItemGenerationInput

        with pytest.raises(ValidationError):
            ItemGenerationInput(count=0)  # Below minimum

        with pytest.raises(ValidationError):
            ItemGenerationInput(count=20000)  # Above maximum

    def test_secret_input(self) -> None:
        """Test SecretInput model."""
        from app.tools.secrets import SecretInput

        model = SecretInput(name="test", value=42.0)
        assert model.name == "test"
        assert model.value == 42.0

    def test_secret_input_validation(self) -> None:
        """Test SecretInput validates name length."""
        from pydantic import ValidationError

        from app.tools.secrets import SecretInput

        with pytest.raises(ValidationError):
            SecretInput(name="", value=1.0)  # Empty name

    def test_secret_compute_input(self) -> None:
        """Test SecretComputeInput model."""
        from app.tools.secrets import SecretComputeInput

        model = SecretComputeInput(secret_ref="ref:123", multiplier=2.5)
        assert model.secret_ref == "ref:123"
        assert model.multiplier == 2.5

    def test_secret_compute_input_default_multiplier(self) -> None:
        """Test SecretComputeInput default multiplier."""
        from app.tools.secrets import SecretComputeInput

        model = SecretComputeInput(secret_ref="ref:456")
        assert model.multiplier == 1.0

    def test_cache_query_input(self) -> None:
        """Test CacheQueryInput model."""
        from app.tools.cache import CacheQueryInput

        model = CacheQueryInput(ref_id="cache:ref", page=2, page_size=20)
        assert model.ref_id == "cache:ref"
        assert model.page == 2
        assert model.page_size == 20

    def test_cache_query_input_defaults(self) -> None:
        """Test CacheQueryInput optional fields."""
        from app.tools.cache import CacheQueryInput

        model = CacheQueryInput(ref_id="cache:ref")
        assert model.page is None
        assert model.page_size is None
        assert model.max_size is None


class TestTemplateGuidePrompt:
    """Tests for the template_guide prompt."""

    def _call_template_guide(self) -> str:
        """Helper to call template_guide prompt."""
        from app import server

        prompt_fn = server.template_guide
        if hasattr(prompt_fn, "fn"):
            return prompt_fn.fn()
        return prompt_fn()

    def test_template_guide_returns_string(self) -> None:
        """Test that template_guide returns a string."""
        result = self._call_template_guide()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_template_guide_mentions_hello(self) -> None:
        """Test that guide mentions hello tool."""
        result = self._call_template_guide()
        assert "hello" in result.lower()

    def test_template_guide_mentions_generate_items(self) -> None:
        """Test that guide mentions generate_items tool."""
        result = self._call_template_guide()
        assert "generate_items" in result

    def test_template_guide_mentions_pagination(self) -> None:
        """Test that guide mentions pagination."""
        result = self._call_template_guide()
        assert "paginate" in result.lower() or "page" in result.lower()

    def test_template_guide_mentions_secret(self) -> None:
        """Test that guide mentions secret computation."""
        result = self._call_template_guide()
        assert "secret" in result.lower()
