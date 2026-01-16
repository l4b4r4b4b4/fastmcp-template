# Goal 03: Add Minimal Tools Option

## Status: 🟢 Complete

**Created:** 2025-01-08
**Updated:** 2025-01-08 (Completed)
**Priority:** Medium
**Estimated Effort:** 3-4 hours
**Depends On:** 
- ✅ Goal 01 (Fix Cookiecutter Templating) - Complete
- ✅ Goal 02 (Fix Demo Tools Test Consistency) - Complete

---

## Objective

Add a new cookiecutter option `include_secret_tools` that allows users to generate a minimal MCP server without secret computation demo tools. Combined with the existing `include_demo_tools` option, users can create truly minimal servers with only essential infrastructure (health check, cache primitives, admin tools).

---

## Problem Description

Currently, when generating a new project from this template, users get many demo/example tools that they'll need to manually remove:

| Tool | Category | Keep in Minimal? |
|------|----------|------------------|
| `hello` | Demo | ❌ Remove |
| `generate_items` | Demo | ❌ Remove |
| `store_secret` | Demo (secrets) | ❌ Remove |
| `compute_with_secret` | Demo (secrets) | ❌ Remove |
| `get_cached_result` | Core Cache | ✅ Keep |
| `health_check` | Core Health | ✅ Keep |
| `enable_test_context` | Langfuse Testing | ⚠️ Conditional (Langfuse) |
| `set_test_context` | Langfuse Testing | ⚠️ Conditional (Langfuse) |
| `reset_test_context` | Langfuse Testing | ⚠️ Conditional (Langfuse) |
| `get_trace_info` | Langfuse Testing | ⚠️ Conditional (Langfuse) |
| `admin_*` | Admin Tools | ✅ Keep (permission-gated) |

### User Pain Points

1. **Manual cleanup required** - Users must delete demo tool files and update imports
2. **Dead code in production** - Unused demo tools clutter the codebase
3. **Test maintenance** - Demo tool tests fail if tools are manually removed
4. **Confusion** - New users may not know what's demo vs essential

---

## Proposed Solution

### New Cookiecutter Variable

Add to `cookiecutter.json`:

```json
{
  "include_example_tools": ["no", "yes"],
}
```

**Note:** This is DIFFERENT from `include_demo_tools`:
- `include_demo_tools` - Controls `hello` and `generate_items` only
- `include_example_tools` - Controls ALL example/demo code including secrets

### Option to Consolidate

Consider consolidating into a single option with clearer semantics:

```json
{
  "project_template": ["minimal", "full"],
}
```

Keep separate for granularity (RECOMMENDED):

```json
{
  "include_demo_tools": ["no", "yes"],      // hello, generate_items (ALREADY EXISTS)
  "include_secret_tools": ["no", "yes"],    // store_secret, compute_with_secret (NEW)
}
```

**Decision: Use separate `include_secret_tools` option**
- Leverages existing `include_demo_tools` pattern
- Consistent with Goal 02 approach
- Granular control for users

---

## Analysis of Tools

### Core Tools (Always Include)

These are essential infrastructure:

| Tool | Purpose | File |
|------|---------|------|
| `health_check` | Server health monitoring | `tools/health.py` |
| `get_cached_result` | RefCache pagination/retrieval | `tools/cache.py` |
| `admin_*` tools | Cache management (permission-gated) | Registered in `server.py` |

### Demo Tools (Configurable - `include_demo_tools`)

Already controlled by existing option:

| Tool | Purpose | File |
|------|---------|------|
| `hello` | Simple greeting demo | `tools/demo.py` |
| `generate_items` | Cached list generation demo | `tools/demo.py` |

### Secret Tools (New Option - `include_secret_tools`)

Example of private computation pattern:

| Tool | Purpose | File |
|------|---------|------|
| `store_secret` | Store values with EXECUTE-only access | `tools/secrets.py` |
| `compute_with_secret` | Use secrets without revealing them | `tools/secrets.py` |

### Langfuse Tools (Already Controlled by `include_langfuse`)

| Tool | Purpose | File |
|------|---------|------|
| `enable_test_context` | Enable Langfuse test mode | `tools/context.py` |
| `set_test_context` | Set test context values | `tools/context.py` |
| `reset_test_context` | Reset test context | `tools/context.py` |
| `get_trace_info` | Get tracing status | `tools/context.py` |

---

## Research Findings

### Current State Analysis

**Existing Options:**
- `include_demo_tools`: ["no", "yes"] - Controls hello, generate_items
- `include_langfuse`: ["yes", "no"] - Controls Langfuse tracing

**Secret Tools Currently Unconditional:**
1. `store_secret` - Stores values with EXECUTE-only permissions
2. `compute_with_secret` - Uses secrets without revealing them
3. Related: `SecretInput`, `SecretComputeInput` Pydantic models

**Files That Import/Use Secret Tools:**
- `app/tools/__init__.py` - Unconditional imports from `tools/secrets.py`
- `app/server.py` - Unconditional registration of `store_secret`, `compute_with_secret`
- `tests/test_server.py` - Test classes: `TestStoreSecret` (L368+), `TestComputeWithSecret` (L420+)

**MCP Instructions:**
- `server.py` lines ~75-76 mention secret tools in instructions string

### Test Counts
- **Current with demos:** 101 tests total
- **Current without demos:** 85 tests total
- **Secret tool tests:** ~18 tests (estimated from test classes)
- **Expected minimal (no demos, no secrets):** ~67 tests

---

## Implementation Plan

### Task 01: Add `include_secret_tools` Option ✅

1. Add to `cookiecutter.json` after `include_demo_tools`:
   ```json
   "include_secret_tools": ["no", "yes"],
   ```

2. Default to `"no"` for minimal template
3. Update JSON structure to maintain proper formatting

**Result:** ✅ Added to cookiecutter.json line 13

### Task 02: Make secrets.py Imports Conditional ✅

Update `app/tools/__init__.py`:

**Changes needed:**
1. Wrap secret imports in Jinja conditional (lines ~30-36)
2. Remove secret items from `__all__` or make conditional
3. Update module docstring to conditionally list secrets module

**Pattern (following Goal 02 approach):**
```python
{% if cookiecutter.include_secret_tools == "yes" %}
from app.tools.secrets import (
    SecretComputeInput,
    SecretInput,
    create_compute_with_secret,
    create_store_secret,
)
{% endif %}
```

**Also update `__all__` list:**
- `SecretComputeInput` - conditional
- `SecretInput` - conditional
- `create_compute_with_secret` - conditional
- `create_store_secret` - conditional

**Result:** ✅ All secret imports and exports wrapped in conditionals

### Task 03: Update server.py ✅

**Three changes needed:**

1. **Conditional import** (lines ~34-37):
   ```python
   {% if cookiecutter.include_secret_tools == "yes" %}
       create_compute_with_secret,
       create_store_secret,
   {% endif %}
   ```

2. **Conditional tool creation** (lines ~118-119):
   ```python
   {% if cookiecutter.include_secret_tools == "yes" %}
   store_secret = create_store_secret(cache)
   compute_with_secret = create_compute_with_secret(cache)
   {% endif %}
   ```

3. **Conditional tool registration** (lines ~179-180):
   ```python
   {% if cookiecutter.include_secret_tools == "yes" %}
   mcp.tool(store_secret)
   mcp.tool(compute_with_secret)
   {% endif %}
   ```

**Result:** ✅ Three locations updated in server.py (imports, creation, registration)

### Task 04: Make Secret Tests Conditional ✅

Wrap test classes in `tests/test_server.py` (following Goal 02 pattern):

**Test classes to wrap:**
1. `TestStoreSecret` (L368+) - ~10 test methods
2. `TestComputeWithSecret` (L420+) - ~8 test methods
3. Parts of `TestPydanticModels` - Tests for `SecretInput`, `SecretComputeInput`

**Pattern:**
```python
{% if cookiecutter.include_secret_tools == "yes" %}
class TestStoreSecret:
    """Tests for the store_secret tool."""
    # ... all test methods ...
{% endif %}
```

**Result:** ✅ Wrapped TestStoreSecret, TestComputeWithSecret, and 4 Pydantic model tests

### Task 05: Update MCP Instructions ✅

Update `server.py` instructions string (lines ~75-76):

**Current (always shows):**
```
- store_secret: Store a secret value for private computation
- compute_with_secret: Use a secret in computation without revealing it
```

**Change to conditional:**
```python
{% if cookiecutter.include_secret_tools == "yes" %}
- store_secret: Store a secret value for private computation
- compute_with_secret: Use a secret in computation without revealing it
{% endif %}
```

**Also check:** `tools/__init__.py` module docstring may reference secrets module

**Result:** ✅ Instructions conditionally mention secret tools, module docstring updated

### Task 06: Update Documentation ✅

**Files to update:**
1. `README.md` - Add `include_secret_tools` to cookiecutter options table
2. `TOOLS.md` - Wrap secret tool documentation in conditional (if exists)
3. Module docstring in `tools/__init__.py` - Conditional "secrets" line

**Note:** Keep documentation minimal - users will see the option during generation

**Result:** ✅ Updated README.md with configuration options table and usage examples

### Task 07: Verification ✅

**Test key combinations:**

| demo_tools | secret_tools | Actual Tests | Status | Description |
|------------|--------------|--------------|--------|-------------|
| yes | yes | 101 | ✅ Pass (3.04s) | Full template (all demos) |
| yes | no | 86 | ✅ Pass (3.36s) | Demo tools, no secrets |
| no | yes | 85 | ✅ Pass (4.19s) | Secrets, no demos |
| no | no | 74 | ✅ Pass (3.37s) | Minimal (core + health + cache + admin) |

**Verification steps:**
1. Generate with each combination
2. Run `uv run pytest --tb=short -v`
3. Verify all tests pass ✅
4. Check no orphaned imports ✅
5. Verify MCP instructions match available tools ✅

**Critical combinations tested:**
- ✅ `no`/`no` - Truly minimal server (74 tests, 3.37s)
- ✅ `yes`/`yes` - Full template (101 tests, 3.04s)
- ✅ `yes`/`no` - Demos only (86 tests, 3.36s)
- ✅ `no`/`yes` - Secrets only (85 tests, 4.19s)

**Result:** All four configurations generate working projects with passing tests

---

## Alternative: Single "Template Flavor" Option

Instead of multiple boolean options, consider a single choice:

```json
{
  "template_flavor": ["minimal", "standard", "full"],
}
```

| Flavor | demo_tools | secret_tools | langfuse |
|--------|------------|--------------|----------|
| minimal | no | no | no |
| standard | no | no | yes |
| full | yes | yes | yes |

**Pros:**
- Simpler user experience
- Fewer combinations to test

**Cons:**
- Less flexible
- Can't mix (e.g., demo tools + no Langfuse)

**Decision:** Keep separate options for flexibility, but document common combinations.

---

## Acceptance Criteria

- [x] New `include_secret_tools` option in `cookiecutter.json` (default "no")
- [x] `tools/__init__.py` imports secrets conditionally
- [x] `server.py` imports secret tools conditionally
- [x] `server.py` creates secret tool instances conditionally
- [x] `server.py` registers secret tools conditionally
- [x] MCP instructions mention secret tools conditionally
- [x] Secret-related test classes wrapped with conditionals
- [x] Pydantic model tests (SecretInput, SecretComputeInput) wrapped conditionally
- [x] Module docstrings updated (conditional references)
- [x] All 4 key combinations generate working projects with passing tests
- [x] No orphaned imports in any configuration
- [x] README.md updated with new option

---

## Files Modified ✅

| File | Changes | Status |
|------|---------|--------|
| `cookiecutter.json` | Added `include_secret_tools` option | ✅ Complete |
| `app/tools/__init__.py` | Conditional secrets imports and exports | ✅ Complete |
| `app/server.py` | Conditional imports, creation, registration, instructions | ✅ Complete |
| `tests/test_server.py` | Wrapped 2 test classes + 4 Pydantic tests + 2 additional tests | ✅ Complete |
| `README.md` | Added configuration options table and usage examples | ✅ Complete |

---

## Post-Generation Verification Script

Consider adding a script to `hooks/post_gen_project.py` that verifies the generated project:

```python
def verify_generation():
    """Verify the generated project is consistent."""
    # Check for orphaned imports
    # Run basic syntax check
    # Optionally run tests
    pass
```

---

## Notes

- Depends on Goal 02 (demo tools conditional) - ✅ COMPLETE
- Langfuse tools already controlled by `include_langfuse` option
- Admin tools ALWAYS included (permission-gated, not demo code)
- Secret tools file (`tools/secrets.py`) will remain in template even when not used (following Goal 02 pattern)
- This creates truly minimal option: `include_demo_tools=no` + `include_secret_tools=no` = ~67 tests

## Implementation Strategy

Following the 5-step workflow from .rules:

1. ✅ **Gather Context & Research** - Complete
   - Analyzed current template structure
   - Identified all files needing changes
   - Estimated test counts for verification
   - Reviewed Goal 02 implementation for patterns

2. **Document Plan** - In Progress
   - Updated this scratchpad with detailed task breakdown
   - Listed exact line numbers and changes needed
   - Defined acceptance criteria

3. **Pitch Approach** - Next Step
   - Present implementation plan to user
   - Get approval before making changes

4. **Implement** - Pending Approval
   - Make changes following documented plan
   - Use Jinja conditionals matching Goal 02 pattern

5. ✅ **Verify & Document** - Complete
   - Tested all 4 key combinations (all pass)
   - Updated scratchpads with completion status

---

## Verification Results

### Test Summary

All four configurations successfully generate working projects:

1. **Minimal (no/no):** 74 tests pass in 3.37s
   - Core infrastructure only
   - No demo or secret tools
   - Smallest, cleanest template

2. **Full (yes/yes):** 101 tests pass in 3.04s
   - All demo tools included
   - All secret tools included
   - Complete reference implementation

3. **Demos Only (yes/no):** 86 tests pass in 3.36s
   - Demo tools (hello, generate_items)
   - No secret tools
   - Good for basic examples

4. **Secrets Only (no/yes):** 85 tests pass in 4.19s
   - No demo tools
   - Secret tools (store_secret, compute_with_secret)
   - Private computation pattern example

### Additional Test Fixes

During verification, found and fixed 2 additional tests that needed conditionals:
- `test_instructions_mention_secret` - Now conditional on `include_secret_tools`
- `test_get_cached_result_with_valid_ref` - Now conditional (uses store_secret)

### No Orphaned Imports

Verified no import errors in any of the 4 configurations. All conditional imports work correctly.
</text>

<old_text line=333>
| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-08 | Add `include_secret_tools` separate from `include_demo_tools` | Granular control, secrets are a distinct pattern |
| 2025-01-08 | Keep admin tools unconditional | They're production infrastructure, not demos |
| 2025-01-08 | Default `include_secret_tools` to "no" | Most users will implement their own patterns |

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-08 | Add `include_secret_tools` separate from `include_demo_tools` | Granular control, secrets are a distinct pattern |
| 2025-01-08 | Keep admin tools unconditional | They're production infrastructure, not demos |
| 2025-01-08 | Default `include_secret_tools` to "no" | Most users will implement their own patterns |