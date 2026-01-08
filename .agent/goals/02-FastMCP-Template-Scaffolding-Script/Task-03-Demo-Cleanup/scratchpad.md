# Task 03: Demo Tool Cleanup Logic

**Status:** ⚪ Not Started
**Created:** 2025-01-08
**Last Updated:** 2025-01-08

---

## Objective

Implement the core logic to remove all demo tool references from the fastmcp-template. This includes parsing Python files with AST, removing demo tool definitions, cleaning up imports, removing tests, and updating documentation to eliminate all traces of template demo code.

---

## Scope

This task is the heart of the scaffolding tool - it transforms a template full of demo code into a clean starting point for real projects.

**Files to Clean:**
- `app/server.py` - Remove demo tool registrations and imports
- `app/tools/demo.py` - Delete entire file
- `app/tools/secrets.py` - Delete entire file
- `app/tools/__init__.py` - Remove demo exports
- `app/prompts/__init__.py` - Remove demo tool examples
- `tests/test_server.py` - Remove demo tool test classes
- `README.md` - Remove demo tool references (optional)

**Demo Tools to Remove:**
- `hello` - Simple greeting tool
- `generate_items` - Item generation with caching
- `store_secret` - Secret storage demo
- `compute_with_secret` - Private computation demo

---

## Implementation Plan

### Approach: AST-Based Code Manipulation

Use Python's `ast` module to parse, modify, and regenerate Python files safely.

**Why AST over Regex:**
- Type-safe and structure-aware
- Handles nested code correctly
- Preserves code formatting (with black/ruff)
- Less error-prone

---

## Success Criteria

- [ ] All demo tool imports removed from server.py
- [ ] All demo tool registrations removed (@mcp.tool decorators)
- [ ] Demo tool files deleted (demo.py, secrets.py)
- [ ] Demo tests removed from test_server.py
- [ ] Server name updated throughout
- [ ] Prompts updated with generic starter text
- [ ] Generated code passes linting
- [ ] Generated code passes all tests
- [ ] No references to "demo", "hello", "generate_items", etc. remain

---

## Notes

This is the most complex task - involves safe code transformation without breaking the project structure.
