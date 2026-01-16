# Task 01: Create cookiecutter.json Configuration

**Status:** 🟡 In Progress
**Priority:** High
**Created:** 2025-01-08
**Effort:** 30 minutes

---

## Objective

Create the `cookiecutter.json` configuration file that defines all template variables, prompts, and defaults for project generation.

---

## Research & Context

### Cookiecutter Best Practices
- **Variable naming:** Use `snake_case` for all variable keys
- **Computed variables:** Use Jinja2 expressions (e.g., `{{ cookiecutter.project_name.lower() }}`)
- **Choice variables:** Use arrays for multiple-choice prompts (first item is default)
- **Order matters:** Variables appear in prompts in the order defined
- **Validation:** Use `pre_gen_project.py` hook for complex validation

### Template Variables Needed

Based on analysis of `pyproject.toml`, `app/server.py`, and other files:

1. **project_name** - Human-readable name (e.g., "Optimization MCP")
2. **project_slug** - Package name (e.g., "optimization-mcp")
3. **project_description** - One-line summary for pyproject.toml
4. **author_name** - Full name for pyproject.toml authors
5. **author_email** - Email for pyproject.toml authors
6. **python_version** - Minimum Python version (default: "3.12")
7. **include_demo_tools** - Keep demo tools? ["no", "yes"]
8. **include_langfuse** - Include Langfuse tracing? ["yes", "no"]
9. **github_username** - For Docker images and URLs

### Variable Dependencies

- `project_slug` is computed from `project_name`
- Docker image names use `github_username` and `project_slug`
- Entry point uses `project_slug` with underscores instead of hyphens

---

## Implementation Plan

### Step 1: Define Core Variables
```json
{
  "project_name": "FastMCP Template",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-').replace('_', '-') }}",
  "project_description": "A FastMCP server with RefCache integration",
  "author_name": "Your Name",
  "author_email": "you@example.com"
}
```

### Step 2: Add Technical Configuration
```json
{
  "python_version": "3.12",
  "fastmcp_version": ">=2.14.0",
  "mcp_refcache_version": ">=0.1.0"
}
```

### Step 3: Add Feature Flags
```json
{
  "include_demo_tools": ["no", "yes"],
  "include_langfuse": ["yes", "no"]
}
```

### Step 4: Add GitHub/Docker Variables
```json
{
  "github_username": "yourusername",
  "__docker_image": "{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}"
}
```

Note: Variables starting with `__` are private (not prompted)

---

## Files to Create/Modify

- ✅ `fastmcp-template/cookiecutter.json` (created)

---

## Testing Strategy

1. **Validate JSON syntax** - Use `python -m json.tool cookiecutter.json`
2. **Test variable rendering** - Run `cookiecutter . --no-input`
3. **Test with custom values** - Run `cookiecutter .` and answer prompts
4. **Verify computed variables** - Check that `project_slug` is correctly derived

---

## Acceptance Criteria

- [x] `cookiecutter.json` exists at repository root
- [x] All 9 core variables defined with sensible defaults (plus 8 dependency/private vars = 17 total)
- [x] `project_slug` correctly computed from `project_name`
- [x] Choice variables use array syntax with default first
- [x] File passes JSON validation (`python -m json.tool cookiecutter.json`)
- [x] Variables are in logical prompt order

---

## Notes

- Keep defaults beginner-friendly (e.g., `include_demo_tools: "no"`)
- Use `include_langfuse: "yes"` as default since it's opt-in via env vars
- `python_version` should match what's in current `pyproject.toml`
- Consider adding `__year` for copyright notices in future task

---

## Completion Log

### 2025-01-08 - Initial Implementation ✅
- Created `cookiecutter.json` with all required variables (17 total)
- Used Jinja2 expression for `project_slug` computation from `project_name`
- Added computed `__project_slug_underscore` for Python module names
- Added computed `__docker_image` for Docker image references
- Added computed `__year` for copyright notices
- Included dependency version variables (fastmcp, mcp_refcache, langfuse, pydantic)
- Set defaults based on current template values (pyproject.toml v0.0.3)
- Validated JSON syntax with `python -m json.tool` - PASSED ✓
- Installed cookiecutter 2.6.0 for testing (uv tool install)
- Ready for Task 02: Repository restructuring

### Variables Summary
**Core prompts (9):**
1. project_name - Human-readable name
2. project_slug - Computed from project_name
3. project_description - One-line summary
4. author_name - Full name
5. author_email - Email address
6. python_version - Minimum Python (default: 3.12)
7. include_demo_tools - Keep demos? (default: no)
8. include_langfuse - Include tracing? (default: yes)
9. github_username - GitHub user/org

**Dependency versions (4):**
- fastmcp_version: >=2.14.0
- mcp_refcache_version: >=0.1.0
- langfuse_version: >=3.10.0
- pydantic_version: >=2.10.0

**Private/computed (4):**
- __project_slug_underscore - For Python imports (my-app → my_app)
- __docker_image - Full Docker image name
- __year - Current year for copyrights