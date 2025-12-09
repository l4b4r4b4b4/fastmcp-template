"""Pytest configuration and fixtures for fastmcp-template tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from mcp_refcache import PreviewConfig, PreviewStrategy, RefCache, SizeMode

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def cache() -> Generator[RefCache, None, None]:
    """Create a fresh RefCache instance for testing."""
    test_cache = RefCache(
        name="test_fastmcp_template",
        default_ttl=3600,
        preview_config=PreviewConfig(
            size_mode=SizeMode.CHARACTER,
            max_size=500,
            default_strategy=PreviewStrategy.SAMPLE,
        ),
    )
    yield test_cache
    # Cleanup after test
    test_cache.clear()


@pytest.fixture
def sample_items() -> list[dict[str, int | str]]:
    """Generate sample items for testing."""
    return [{"id": i, "name": f"item_{i}", "value": i * 10} for i in range(100)]
