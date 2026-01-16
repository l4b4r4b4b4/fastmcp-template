# Goal 07: Add Example Integrations

## Status: ⚪ Not Started

**Created:** 2025-01-08
**Updated:** 2025-01-08
**Priority:** Medium
**Estimated Effort:** 4-6 hours
**Depends On:** 
- ✅ Goal 01 (Fix Cookiecutter Templating) - Complete
- ✅ Goal 02 (Fix Demo Tools Test Consistency) - Complete
- ✅ Goal 03 (Add Minimal Tools Option) - Complete

---

## Objective

Add optional example integrations that demonstrate real-world patterns for common use cases. These would be opt-in via cookiecutter configuration and provide working examples of database queries, API calls, file operations, and external service integrations.

---

## Problem Description

Current demo tools are too simple:
- ❌ `hello` - Just returns a greeting (trivial)
- ❌ `generate_items` - Creates fake data (not realistic)
- ❌ Secret tools - Abstract pattern demonstration

Users need examples of:
- ✅ Database queries (PostgreSQL, SQLite)
- ✅ API calls with rate limiting
- ✅ File operations (read, search, process)
- ✅ External service integration (Slack, GitHub, etc.)
- ✅ Error handling patterns
- ✅ Authentication flows

---

## Proposed Solution

Add `include_examples` cookiecutter option with categories:

```json
{
  "include_examples": ["none", "database", "api", "filesystem", "all"],
}
```

Each example category includes:
- Working tool implementation
- Tests with mocking
- Documentation
- Configuration examples
- Error handling patterns

---

## Example Categories

### 1. Database Examples (`@database`)

**Tools:**
- `query_database` - Execute SQL queries with parameter binding
- `search_records` - Full-text search with pagination
- `upsert_data` - Insert/update with conflict resolution

**Features:**
- Connection pooling
- Query parameterization (SQL injection prevention)
- Transaction handling
- Error recovery
- Schema migrations example

**Backends:**
- PostgreSQL (asyncpg)
- SQLite (aiosqlite)
- Configurable via environment

**Files:**
```
app/tools/examples/
├── database.py
├── db_config.py
└── migrations/
    └── 001_initial_schema.sql

tests/
└── test_database_examples.py

docs/
└── DATABASE_EXAMPLES.md
```

---

### 2. API Examples (`@api`)

**Tools:**
- `fetch_api_data` - HTTP GET with retry logic
- `post_to_api` - HTTP POST with authentication
- `stream_api_events` - SSE/WebSocket streaming

**Features:**
- Rate limiting (token bucket, sliding window)
- Exponential backoff retry
- Circuit breaker pattern
- Request/response caching
- API key management
- OAuth 2.0 flow example

**Libraries:**
- `httpx` for async HTTP
- `tenacity` for retries
- `limits` for rate limiting

**Files:**
```
app/tools/examples/
├── api_client.py
├── rate_limiter.py
└── auth.py

tests/
└── test_api_examples.py
```

---

### 3. Filesystem Examples (`@filesystem`)

**Tools:**
- `search_files` - Find files with glob patterns
- `read_file_content` - Read and parse various formats
- `process_directory` - Batch file operations
- `watch_directory` - Monitor file changes

**Features:**
- Path validation (prevent directory traversal)
- Sandboxing (restrict to allowed directories)
- File type detection
- Format parsing (JSON, YAML, CSV, Markdown)
- Streaming for large files
- Content caching

**Files:**
```
app/tools/examples/
├── filesystem.py
├── file_parsers.py
└── validators.py

tests/
└── test_filesystem_examples.py
```

---

### 4. External Service Examples (`@services`)

**Integrations:**

**Slack:**
- `send_slack_message` - Post to channels
- `search_slack_history` - Query message history
- `react_to_message` - Add emoji reactions

**GitHub:**
- `search_code` - Code search across repos
- `create_issue` - File issues programmatically
- `get_pr_diff` - Retrieve PR changes

**Email (SMTP/IMAP):**
- `send_email` - Send with attachments
- `fetch_emails` - Retrieve and parse
- `search_inbox` - Query with filters

**Features:**
- OAuth integration patterns
- Webhook handling
- Rate limit respect
- Error handling
- Pagination

---

## Implementation Plan

### Task 01: Add Example Configuration

**File:** `cookiecutter.json`

**Add:**
```json
{
  "include_examples": ["none", "database", "api", "filesystem", "services", "all"],
  
  // Sub-options (only if include_examples != none)
  "example_database_backend": ["postgresql", "sqlite", "both"],
  "example_api_provider": ["httpbin", "jsonplaceholder", "custom"],
  "example_service_integrations": {
    "slack": false,
    "github": false,
    "email": false
  }
}
```

### Task 02: Create Example Tool Structure

**Directory structure:**
```
{{cookiecutter.project_slug}}/
├── app/
│   └── tools/
│       ├── examples/  # New directory
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── api_client.py
│       │   ├── filesystem.py
│       │   └── services/
│       │       ├── __init__.py
│       │       ├── slack.py
│       │       ├── github.py
│       │       └── email.py
│       ├── demo.py  # Existing
│       └── secrets.py  # Existing
```

### Task 03: Implement Database Examples

**File:** `app/tools/examples/database.py`

**Implementation:**
```python
from typing import Any
import os
from pydantic import BaseModel, Field

class DatabaseQuery(BaseModel):
    """Input for database queries."""
    sql: str = Field(..., description="SQL query to execute")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Query parameters"
    )
    limit: int = Field(default=100, le=1000)

async def query_database(
    query: DatabaseQuery,
    cache: RefCache,
) -> dict[str, Any]:
    """Execute database query with connection pooling.
    
    Features:
    - Parameter binding (SQL injection prevention)
    - Connection pooling
    - Query timeout
    - Result caching
    - Error handling
    
    Examples:
        Query users:
        ```json
        {
          "sql": "SELECT * FROM users WHERE created_at > :date",
          "params": {"date": "2024-01-01"},
          "limit": 100
        }
        ```
    """
    # Implementation with asyncpg/aiosqlite
    # Connection pooling
    # Error handling
    # Result caching
    pass
```

### Task 04: Implement API Examples

**File:** `app/tools/examples/api_client.py`

**Implementation:**
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from limits import storage, strategies

class APIRequest(BaseModel):
    """Input for API requests."""
    url: str
    method: str = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] | None = None
    
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_api_data(
    request: APIRequest,
    cache: RefCache,
) -> dict[str, Any]:
    """Fetch data from external API with retry logic.
    
    Features:
    - Exponential backoff retry
    - Rate limiting (respects API limits)
    - Response caching
    - Timeout handling
    - Circuit breaker
    
    Examples:
        Fetch JSON data:
        ```json
        {
          "url": "https://api.example.com/data",
          "method": "GET",
          "headers": {"Authorization": "Bearer ${API_KEY}"}
        }
        ```
    """
    # Implementation with httpx
    # Rate limiting
    # Circuit breaker
    # Caching
    pass
```

### Task 05: Add Tests for Examples

**File:** `tests/test_examples_database.py`

**Test patterns:**
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
async def mock_db_connection():
    """Mock database connection for testing."""
    conn = AsyncMock()
    conn.fetch.return_value = [
        {"id": 1, "name": "Test User"}
    ]
    return conn

async def test_query_database_success(mock_db_connection):
    """Test successful database query."""
    # Test implementation
    pass

async def test_query_database_sql_injection_prevention():
    """Test that SQL injection is prevented."""
    # Test parameterization
    pass

async def test_query_database_connection_error():
    """Test connection error handling."""
    # Test error recovery
    pass
```

### Task 06: Add Documentation

**Files:**
- `docs/EXAMPLES_DATABASE.md` - Database patterns
- `docs/EXAMPLES_API.md` - API integration patterns
- `docs/EXAMPLES_FILESYSTEM.md` - File operation patterns
- `docs/EXAMPLES_SERVICES.md` - External service patterns

**Each includes:**
- Overview and use cases
- Configuration guide
- Code examples
- Best practices
- Common pitfalls
- Testing strategies

### Task 07: Update README

**File:** `README.md` (template repo)

**Add section:**
```markdown
## Example Integrations

The template can include working examples of common integration patterns:

### Database Integration
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template \
  --no-input \
  include_examples=database \
  example_database_backend=postgresql
```

Includes:
- Connection pooling
- Query parameterization
- Transaction handling
- Migration examples

### API Integration
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template \
  --no-input \
  include_examples=api
```

Includes:
- Rate limiting
- Retry logic
- Circuit breaker
- Authentication patterns
```

---

## Acceptance Criteria

- [ ] `include_examples` option added to cookiecutter.json
- [ ] Database examples implemented with tests
- [ ] API examples implemented with retry/rate limiting
- [ ] Filesystem examples with security validation
- [ ] At least 2 external service examples
- [ ] All examples have comprehensive tests
- [ ] Documentation for each example category
- [ ] Examples are opt-in (don't clutter minimal config)
- [ ] Generated projects with examples pass all tests
- [ ] README explains example usage

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `cookiecutter.json` | Update | Add examples configuration |
| `app/tools/examples/*.py` | Create | Example implementations |
| `tests/test_examples_*.py` | Create | Example tests |
| `docs/EXAMPLES_*.md` | Create | Example documentation |
| `README.md` (template repo) | Update | Document examples |
| `.env.example` | Update | Add example env vars |

---

## Configuration Matrix

| Option | Database | API | Filesystem | Services | Tests |
|--------|----------|-----|------------|----------|-------|
| none | ❌ | ❌ | ❌ | ❌ | 74/85/86/101 |
| database | ✅ | ❌ | ❌ | ❌ | +~20 tests |
| api | ❌ | ✅ | ❌ | ❌ | +~15 tests |
| filesystem | ❌ | ❌ | ✅ | ❌ | +~12 tests |
| services | ❌ | ❌ | ❌ | ✅ | +~10 tests |
| all | ✅ | ✅ | ✅ | ✅ | +~57 tests |

---

## Benefits

**For Users:**
- ✅ Real-world patterns shown
- ✅ Copy-paste starting points
- ✅ Best practices demonstrated
- ✅ Common pitfalls avoided
- ✅ Learning by example

**For Template:**
- ✅ More comprehensive
- ✅ Better onboarding
- ✅ Competitive advantage
- ✅ Community contributions easier

---

## Implementation Notes

- Keep examples focused and well-documented
- Mock external dependencies in tests
- Use environment variables for configuration
- Include security best practices
- Demonstrate error handling patterns
- Show async/await patterns throughout
- Include performance considerations
- Add cost/rate limit warnings

---

## Future Enhancements

After initial implementation:
- Add streaming examples (WebSocket, SSE)
- Add background task examples (Celery, RQ)
- Add caching strategy examples (Redis, Memcached)
- Add monitoring/metrics examples (Prometheus)
- Add auth provider examples (Auth0, Clerk)
- Create example compositions (database + API)

---

## Security Considerations

**Database:**
- ✅ Parameter binding (SQL injection prevention)
- ✅ Connection string security
- ✅ Query timeouts
- ✅ Row limit enforcement

**API:**
- ✅ HTTPS only
- ✅ API key security
- ✅ Request validation
- ✅ Response sanitization

**Filesystem:**
- ✅ Path traversal prevention
- ✅ Sandboxing
- ✅ File type validation
- ✅ Size limits

**Services:**
- ✅ OAuth token security
- ✅ Webhook signature verification
- ✅ Rate limit respect
- ✅ PII handling

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-08 | Make examples opt-in | Keeps minimal config clean |
| 2025-01-08 | Four main categories | Covers most use cases |
| 2025-01-08 | Include security patterns | Education + safety |
| 2025-01-08 | Comprehensive tests | Examples must be reliable |
| 2025-01-08 | Separate docs per category | Easier to navigate |