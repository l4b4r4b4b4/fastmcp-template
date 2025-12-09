# GitHub Copilot Instructions for fastmcp-template

This is a FastMCP server project using mcp-refcache for reference-based caching and optional Langfuse tracing.

## Project Structure

- `src/fastmcp_template/` - Main package source code
  - `server.py` - FastMCP server entrypoint
  - `models.py` - Pydantic models
  - `cache.py` - RefCache setup and configuration
  - `tools/` - MCP tool implementations
- `tests/` - Pytest test files
- `docs/` - Extended documentation

## Key Technologies

- **FastMCP**: MCP server framework
- **mcp-refcache**: Reference-based caching for large values
- **Pydantic**: Data validation and models
- **Langfuse** (optional): Observability and tracing

## Code Conventions

### Type Annotations
All functions MUST have complete type annotations:
```python
def process_data(input_data: dict[str, Any], limit: int = 10) -> CacheResponse:
    ...
```

### Pydantic Models
Use Pydantic models for structured data with Field descriptions:
```python
class ToolInput(BaseModel):
    """Input for a tool."""

    query: str = Field(..., description="The search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max results")
```

### Docstrings
Use Google-style docstrings:
```python
def my_tool(query: str) -> dict[str, Any]:
    """Short description of the tool.

    Args:
        query: What to search for.

    Returns:
        Dictionary containing the results.

    Raises:
        ValueError: If query is empty.
    """
```

### MCP Tool Patterns
Tools should follow this pattern:
```python
@mcp.tool
def my_tool(
    required_param: str,
    optional_param: int = 10,
) -> dict[str, Any]:
    """Tool description for the MCP client.

    Args:
        required_param: Description of the parameter.
        optional_param: Optional parameter with default.

    Returns:
        Result dictionary.
    """
    # Implementation
    return {"result": "value"}
```

### RefCache Integration
For large return values, use RefCache:
```python
from mcp_refcache import CacheResponse

@mcp.tool
def generate_large_data(count: int = 100) -> dict[str, Any]:
    """Generate data that may be large."""
    data = [{"id": i, "value": f"item_{i}"} for i in range(count)]

    response: CacheResponse = cache.set(
        key=f"data_{count}",
        value=data,
        namespace="results",
    )

    return {
        "ref_id": response.ref_id,
        "preview": response.preview,
        "total_items": response.total_items,
    }
```

## Testing

- Use pytest with pytest-asyncio for async tests
- Aim for >80% code coverage
- Test both success and error paths

## Dependencies

- Use `uv add <package>` for runtime dependencies
- Use `uv add --dev <package>` for dev dependencies
- Never use pip directly

## Linting & Formatting

- Use Ruff for linting and formatting
- Run `ruff check . --fix && ruff format .` before commits
