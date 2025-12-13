# FastMCP Template - Available Tools

This document describes all MCP tools available in the FastMCP Template server.

## Quick Reference

| Tool | Description | Caching |
|------|-------------|---------|
| `hello` | Simple greeting tool | No |
| `generate_items` | Generate a list of items | Yes (public namespace) |
| `store_secret` | Store a secret value | Yes (user namespace) |
| `compute_with_secret` | Compute with a secret without revealing it | No |
| `get_cached_result` | Retrieve or paginate cached results | N/A |
| `health_check` | Check server health status | No |
| `enable_test_context` | Enable/disable test context mode | No |
| `set_test_context` | Set test context values | No |
| `reset_test_context` | Reset test context to defaults | No |
| `get_trace_info` | Get Langfuse tracing status | No |

---

## Demo Tools

### `hello`

A simple greeting tool that demonstrates basic MCP tool patterns.

**Parameters:**
- `name` (string, optional): The name to greet. Default: `"World"`

**Returns:**
```json
{
  "message": "Hello, World!",
  "server": "fastmcp-template"
}
```

**Example:**
```
hello("Alice")
→ {"message": "Hello, Alice!", "server": "fastmcp-template"}
```

---

### `generate_items`

Generate a list of items with caching support. Demonstrates reference-based caching for large results.

**Parameters:**
- `count` (integer, optional): Number of items to generate. Range: 1-10000. Default: `10`
- `prefix` (string, optional): Prefix for item names. Default: `"item"`

**Returns:**
For small results (≤64 tokens), returns the full data.
For large results, returns a reference with preview:

```json
{
  "ref_id": "public:abc123",
  "preview": [{"id": 0, "name": "item_0", "value": 0}, ...],
  "total_items": 100,
  "preview_strategy": "sample"
}
```

**Example:**
```
generate_items(count=100, prefix="widget")
→ Returns ref_id + preview; use get_cached_result to paginate
```

---

## Secret/Private Computation Tools

### `store_secret`

Store a secret value that agents can use in computations but cannot read.

This demonstrates the EXECUTE permission model - agents can orchestrate computations with the secret without ever seeing its value.

**Parameters:**
- `name` (string, required): Name for the secret (1-100 characters)
- `value` (float, required): The secret numeric value

**Returns:**
```json
{
  "ref_id": "user:secrets:secret_mykey",
  "name": "mykey",
  "message": "Secret 'mykey' stored. Use compute_with_secret.",
  "permissions": {
    "user": "FULL (can read, write, execute)",
    "agent": "EXECUTE only (can use in computation, cannot read)"
  }
}
```

**Example:**
```
store_secret("api_key_hash", 12345.0)
→ Returns ref_id for use with compute_with_secret
```

---

### `compute_with_secret`

Perform computation using a secret value without revealing it.

The agent orchestrates the computation but never sees the actual secret value. Only the result is returned.

**Parameters:**
- `secret_ref` (string, required): Reference ID from `store_secret`
- `multiplier` (float, optional): Value to multiply the secret by. Default: `1.0`

**Returns:**
```json
{
  "result": 24690.0,
  "multiplier": 2.0,
  "secret_ref": "user:secrets:secret_api_key_hash",
  "message": "Computed using secret value (value not revealed)"
}
```

**Example:**
```
# First store a secret
result = store_secret("my_secret", 100.0)

# Then compute with it (agent never sees 100.0)
compute_with_secret(result["ref_id"], multiplier=2.5)
→ {"result": 250.0, ...}
```

---

## Cache Tools

### `get_cached_result`

Retrieve a cached result with optional pagination support.

Use this to:
- Get a preview of a cached value
- Paginate through large lists
- Access the full value of a cached result

**Parameters:**
- `ref_id` (string, required): Reference ID to look up
- `page` (integer, optional): Page number (1-indexed)
- `page_size` (integer, optional): Items per page (1-100)
- `max_size` (integer, optional): Maximum preview size in tokens

**Returns:**
```json
{
  "ref_id": "public:abc123",
  "preview": [...],
  "preview_strategy": "sample",
  "total_items": 100,
  "page": 2,
  "total_pages": 5
}
```

**Example:**
```
# Get page 2 with 20 items per page
get_cached_result("public:abc123", page=2, page_size=20)
```

---

## Health & Status Tools

### `health_check`

Check server health status and configuration.

**Parameters:** None

**Returns:**
```json
{
  "status": "healthy",
  "server": "fastmcp-template",
  "cache": "fastmcp-template",
  "langfuse_enabled": true,
  "test_mode": false
}
```

---

## Context Management Tools

These tools are for testing and demonstrating Langfuse tracing with user/session attribution.

### `enable_test_context`

Enable or disable test context mode for Langfuse attribution demos.

When enabled, all traces will include user_id, session_id, and metadata from MockContext.

**Parameters:**
- `enabled` (boolean, optional): Whether to enable test context mode. Default: `true`

**Returns:**
```json
{
  "test_mode": true,
  "context": {
    "user_id": "demo-user",
    "org_id": "demo-org",
    "agent_id": "demo-agent"
  },
  "langfuse_enabled": true,
  "message": "Test context mode enabled..."
}
```

---

### `set_test_context`

Set test context values for Langfuse attribution demos.

**Parameters:**
- `user_id` (string, optional): User identity (e.g., "alice", "bob")
- `org_id` (string, optional): Organization identity (e.g., "acme", "globex")
- `session_id` (string, optional): Session identifier for grouping traces
- `agent_id` (string, optional): Agent identity (e.g., "claude", "gpt4")

**Returns:**
```json
{
  "context": {
    "user_id": "alice",
    "org_id": "acme",
    "agent_id": "demo-agent"
  },
  "langfuse_attributes": {
    "user_id": "alice",
    "session_id": "chat-001",
    "metadata": {...},
    "tags": [...]
  },
  "message": "Context updated..."
}
```

**Example:**
```
set_test_context(user_id="alice", org_id="acme", session_id="chat-001")
```

---

### `reset_test_context`

Reset test context to default demo values.

**Parameters:** None

**Returns:**
```json
{
  "context": {
    "user_id": "demo-user",
    "org_id": "demo-org",
    "agent_id": "demo-agent"
  },
  "message": "Context reset to default demo values."
}
```

---

### `get_trace_info`

Get information about current Langfuse tracing configuration and context.

**Parameters:** None

**Returns:**
```json
{
  "langfuse_enabled": true,
  "langfuse_host": "https://cloud.langfuse.com",
  "public_key_set": true,
  "secret_key_set": true,
  "test_mode_enabled": true,
  "current_context": {...},
  "langfuse_attributes": {
    "user_id": "alice",
    "session_id": "chat-001",
    "metadata": {...},
    "tags": [...]
  },
  "message": "Traces are being sent to Langfuse..."
}
```

---

## Admin Tools

Admin tools are registered but require admin privileges (disabled by default).

| Tool | Description |
|------|-------------|
| `admin_list_references` | List cached references with filtering |
| `admin_get_reference_info` | Get detailed info about a cached reference |
| `admin_get_cache_stats` | Get cache statistics |
| `admin_delete_reference` | Delete a specific cached reference |
| `admin_clear_namespace` | Clear all references in a namespace |

To enable admin access, override the `is_admin` function in `app/server.py` with your authentication logic.

---

## MCP Prompts

The server also provides two prompts for guidance:

### `template_guide`

Comprehensive guide for using this MCP server template, including:
- Quick start instructions
- Langfuse tracing setup
- Caching examples
- Private computation patterns

### `langfuse_guide`

Detailed guide for Langfuse tracing integration:
- Environment variable setup
- Context propagation
- Viewing traces in Langfuse dashboard
- Best practices
