# Goal 02: Fix Demo Tools & Tests Consistency

## Status: 🟢 Complete

**Created:** 2025-01-08
**Updated:** 2025-01-08 (Completed)
**Priority:** High
**Depends On:** Goal 01 (Fix Cookiecutter Templating) ✅ Complete

**Current Phase:** Complete ✅

---

## Objective

When generating a new project with `include_demo_tools="no"`, the demo tool tests are still included and fail because the demo tools (`hello`, `generate_items`) don't exist. The tests and tools must be consistent with the `include_demo_tools` cookiecutter option.

---

## Problem Description

Currently:
1. **`include_demo_tools` option exists** in `cookiecutter.json` with values `["no", "yes"]`
2. **`app/server.py`** conditionally imports/registers demo tools with `{% if cookiecutter.include_demo_tools == "yes" %}`
3. **`tests/test_server.py`** does NOT have conditional guards - demo tool tests always exist
4. **Result:** When `include_demo_tools="no"`, tests fail because they reference non-existent tools

### Current Test Classes That Need Conditional Guards

From `tests/test_server.py`:

| Test Class | Lines | Should Be Conditional |
|------------|-------|----------------------|
| `TestHelloTool` | L33-54 | ✅ Yes - tests `hello()` |
| `TestGenerateItems` | L284-355 | ✅ Yes - tests `generate_items()` |
| `TestTemplateGuidePrompt` | L703-739 | ⚠️ Partial - mentions hello/generate_items |

### Files That Need Updates

| File | Current State | Required Change |
|------|---------------|-----------------|
| `tests/test_server.py` | No conditionals | Wrap demo tests with `{% if %}` |
| `app/tools/__init__.py` | Unconditional imports | Conditional imports for demo |
| `app/tools/demo.py` | Always included | Consider conditional file removal |

---

## Analysis

### Option A: Wrap Tests in Jinja Conditionals (Recommended)

Add `{% if cookiecutter.include_demo_tools == "yes" %}` around demo-related test classes.

**Pros:**
- Simple to implement
- Consistent with how `server.py` already handles it
- No post-generation hooks needed

**Cons:**
- Test file has Jinja syntax mixed with Python

### Option B: Use Post-Generation Hook to Remove Tests

Add logic to `hooks/post_gen_project.py` to delete demo test classes.

**Pros:**
- Cleaner generated Python files

**Cons:**
- Complex string manipulation or AST parsing
- Fragile if test structure changes
- Harder to maintain

### Decision: Use Option A

Jinja conditionals are already used throughout the template. This is consistent and simple.

---

## Implementation Plan

### Task 01: Update tests/test_server.py ✅ COMPLETE

Wrapped these test classes with `{% if cookiecutter.include_demo_tools == "yes" %}`:

1. ✅ `TestHelloTool` (L33-54)
2. ✅ `TestGenerateItems` (L284-355)
3. ✅ `TestPydanticModels` (L621-711) - Tests ItemGenerationInput
4. ✅ Parts of `TestTemplateGuidePrompt` that mention demo tools (test_template_guide_mentions_hello, test_template_guide_mentions_generate_items)

### Task 02: Update app/tools/__init__.py ✅ COMPLETE

Made demo imports conditional:

```python
{% if cookiecutter.include_demo_tools == "yes" %}
from app.tools.demo import ItemGenerationInput, generate_items, hello
{% endif %}
```

Also updated:
- Docstring tool list (conditional demo line)
- `__all__` list (ItemGenerationInput, generate_items, hello all conditional)

### Task 03: Verification ✅ COMPLETE

**Final Results:**
1. ✅ Generate project with `include_demo_tools="no"` - **85 tests pass** (4.52s)
2. ✅ Generate project with `include_demo_tools="yes"` - **101 tests pass** (4.44s)

**Verification Details:**
- All 101 tests pass when demo tools enabled (85 base + 16 demo)
- All 85 tests pass when demo tools disabled
- No import errors or orphaned references in either configuration
- Template generation works correctly for both options

---

## Acceptance Criteria

- [x] `include_demo_tools="no"` generates project where `pytest` passes (85 tests ✅)
- [x] `include_demo_tools="yes"` generates project where `pytest` passes (101 tests ✅)
- [x] No orphaned imports when demo tools excluded
- [x] `app/tools/__init__.py` conditionally exports demo tools
- [x] `tests/test_server.py` conditionally includes demo tests
- [x] Documentation updated to explain option behavior (README already has usage)

---

## Files Modified ✅

| File | Changes | Status |
|------|---------|--------|
| `tests/test_server.py` | Wrapped `TestHelloTool`, `TestGenerateItems`, `TestPydanticModels`, parts of `TestTemplateGuidePrompt` with conditionals | ✅ Complete |
| `app/tools/__init__.py` | Conditional imports, docstring, and `__all__` for demo tools | ✅ Complete |

---

## Test Matrix

| Option | Expected Tests | Actual Tests | Status |
|--------|----------------|--------------|--------|
| `include_demo_tools="yes"` | 101 (85 base + 16 demo) | 101 | ✅ Pass (4.44s) |
| `include_demo_tools="no"` | 85 (base only) | 85 | ✅ Pass (4.52s) |
| `include_demo_tools="yes"` + `include_langfuse="no"` | Demo tests, no Langfuse tests | Not tested | - |
| `include_demo_tools="no"` + `include_langfuse="no"` | Minimal tests | Not tested | - |

---

## Notes

- The `include_langfuse` option likely has similar issues - verify Langfuse-related tests are also conditional
- `TestTracingModule` and `TestContextManagementTools` may need conditionals based on `include_langfuse`
- Consider creating a test generation verification script

---

## Progress Notes

**2025-01-08 - All Tasks Complete:**
- Wrapped 4 test classes in `tests/test_server.py` with Jinja conditionals
- Made all demo imports conditional in `app/tools/__init__.py`
- Generated project with `include_demo_tools="no"`: **85 tests pass** ✅
- Generated project with `include_demo_tools="yes"`: **101 tests pass** ✅
- Demo tool tests correctly excluded/included based on cookiecutter option
- No import errors or orphaned references in either configuration

**Template Repository Setup:**
- Added minimal `pyproject.toml` to template repo for development tooling
- Added `cookiecutter>=2.6.0` as dev dependency using `uv`
- Template testing now uses `uv run cookiecutter` for consistency
- Follows .rules: Python-first, uv-based dependency management

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-08 | Use Jinja conditionals over post-gen hooks | Simpler, consistent with existing approach |
| 2025-01-08 | Keep demo.py file even when not used | Dead code acceptable, avoids complex file deletion |
| 2025-01-08 | Also wrap TestPydanticModels | Tests ItemGenerationInput which only exists with demos |