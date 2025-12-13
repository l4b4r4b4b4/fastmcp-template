"""Prompts module for FastMCP Template Server.

This module contains MCP prompts that provide guidance and documentation
for using the server features.
"""

from __future__ import annotations

from mcp_refcache.fastmcp import cache_guide_prompt

TEMPLATE_GUIDE = f"""# FastMCP Template Guide

## Langfuse Tracing

All tool calls are traced to Langfuse with user/session attribution.

1. **Enable Test Mode**
   ```
   enable_test_context(True)
   ```

2. **Set User Context**
   ```
   set_test_context(user_id="alice", org_id="acme", session_id="chat-001")
   ```

3. **View Trace Info**
   ```
   get_trace_info()
   ```

4. **View in Langfuse Dashboard**
   - Filter by User: "alice"
   - Filter by Session: "chat-001"
   - Filter by Tags: "fastmcptemplate", "mcprefcache"

## Quick Start

1. **Simple Tool**
   Use `hello` for a basic greeting:
   - `hello("World")` → "Hello, World!"

2. **Generate Items (Caching Demo)**
   Use `generate_items` to create a list:
   - `generate_items(count=100, prefix="widget")`
   - Returns ref_id + preview for large results
   - Cached in the PUBLIC namespace (shared)

3. **Paginate Results**
   Use `get_cached_result` to navigate large results:
   - `get_cached_result(ref_id, page=2, page_size=20)`

## Private Computation

Store values that agents can use but not see:

```
# Store a secret
store_secret("api_key_hash", 12345.0)
# Returns ref_id for the secret

# Use in computation (agent never sees the value)
compute_with_secret(ref_id, multiplier=2.0)
# Returns the result
```

---

{cache_guide_prompt()}
"""

LANGFUSE_GUIDE = """# Langfuse Tracing Guide

## Setup

Set environment variables before starting the server:

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"  # Optional, defaults to cloud
```

## Context Propagation

All tool calls automatically propagate context to Langfuse traces:

1. **User Attribution**
   - `user_id`: Tracks which user made the request
   - `session_id`: Groups related requests into sessions
   - `metadata`: Additional context (org_id, agent_id, cache_namespace)

2. **Testing Context**
   Enable test mode to simulate different users:
   ```
   enable_test_context(True)
   set_test_context(user_id="alice", org_id="acme", session_id="chat-001")
   ```

3. **Cache Operations**
   Cache set/get/resolve operations create child spans that inherit
   user_id and session_id for complete attribution.

## Example Workflow

```python
# 1. Enable test mode and set user
enable_test_context(True)
set_test_context(user_id="alice", session_id="demo-session")

# 2. Generate items (traced with user attribution)
result = generate_items(count=100, prefix="widget")

# 3. Retrieve cached result (same user in trace)
cached = get_cached_result(result["ref_id"])

# 4. Check trace info
info = get_trace_info()
```

## Viewing Traces in Langfuse

1. Go to your Langfuse dashboard
2. Navigate to Traces
3. Filter by:
   - **User**: "alice" (or any user_id you set)
   - **Session**: "demo-session"
   - **Tags**: "fastmcptemplate", "mcprefcache", "cacheset", "cacheget"
   - **Metadata**: orgid, agentid, cachenamespace

## Best Practices

- Enable test mode for demos and testing
- Use meaningful user_id and session_id values
- Check get_trace_info() to verify tracing is working
- Flush traces on server shutdown (handled automatically)
"""


def template_guide() -> str:
    """Guide for using this MCP server template."""
    return TEMPLATE_GUIDE


def langfuse_guide() -> str:
    """Guide for using Langfuse tracing with this server."""
    return LANGFUSE_GUIDE


__all__ = [
    "LANGFUSE_GUIDE",
    "TEMPLATE_GUIDE",
    "langfuse_guide",
    "template_guide",
]
