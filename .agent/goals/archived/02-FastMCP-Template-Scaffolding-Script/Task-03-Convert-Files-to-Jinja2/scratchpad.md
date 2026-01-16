# Task 03: Convert Files to Jinja2 Templates

**Status:** 🟢 Complete
**Priority:** High
**Created:** 2025-01-08
**Completed:** 2025-01-08
**Estimated Effort:** 2-3 hours
**Actual Effort:** 2 hours

---

## Objective

Convert all files in the `{{cookiecutter.project_slug}}/` directory to use Jinja2 template variables and handle conflicting syntax (GitHub Actions, shell variables, etc.).

---

## Research & Context

### Files Requiring Jinja2 Conversion

Based on analysis of template directory:

**High Priority (Critical for generation):**
1. `pyproject.toml` - Project name, description, author, dependencies
2. `app/server.py` - Server name, description, cache namespace
3. `README.md` - Project-specific documentation
4. `.github/workflows/*.yml` - GitHub Actions (escape `${{ }}` syntax)
5. `docker-compose.yml` - Image names
6. `docker/Dockerfile.base` - OCI labels with GitHub URLs

**Medium Priority (Conditional content):**
7. `app/tools/demo.py` - Include if `include_demo_tools == "yes"`
8. `tests/test_server.py` - Demo tests conditional
9. `app/server.py` - Demo tool imports conditional

**Low Priority (Minor changes):**
10. `CONTRIBUTING.md` - Project name references
11. `TOOLS.md` - Project name
12. `docs/README.md` - Project name

### Syntax Conflicts to Handle

**Problem:** GitHub Actions uses `${{ }}` which conflicts with Jinja2's `{{ }}`

**Solutions:**
1. **Escape with raw blocks:**
   ```jinja2
   {% raw %}${{ github.repository_owner }}{% endraw %}
   ```

2. **Use Jinja2 variables instead:**
   ```jinja2
   # Before:
   ${{ github.repository_owner }}/my-app
   
   # After:
   {{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}
   ```

3. **Mix both when needed:**
   ```jinja2
   # Keep GitHub Actions syntax for runtime, use Jinja2 for setup
   image: {{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}:{% raw %}${{ github.sha }}{% endraw %}
   ```

### Conditional File Inclusion

Jinja2 supports conditional file inclusion via filenames:

```
# This file is only copied if condition is true:
{% if cookiecutter.include_demo_tools == "yes" %}app/tools/demo.py{% endif %}
```

However, this is complex. **Better approach:** Use conditional blocks inside files:

```jinja2
{% if cookiecutter.include_demo_tools == "yes" %}
# Demo tool code
def hello(name: str) -> dict:
    ...
{% endif %}
```

---

## Implementation Plan

### Step 1: pyproject.toml
**Variables to replace:**
- `name = "fastmcp-template"` → `name = "{{ cookiecutter.project_slug }}"`
- `description = "..."` → `description = "{{ cookiecutter.project_description }}"`
- `authors = [...]` → `authors = [{ name = "{{ cookiecutter.author_name }}", email = "{{ cookiecutter.author_email }}" }]`
- `requires-python = ">=3.12"` → `requires-python = ">={{ cookiecutter.python_version }}"`
- Entry point: `fastmcp-template = "app.__main__:app"` → `{{ cookiecutter.project_slug }} = "app.__main__:app"`

**Conditional dependencies:**
```jinja2
dependencies = [
    "fastmcp{{ cookiecutter.fastmcp_version }}",
    "mcp-refcache{{ cookiecutter.mcp_refcache_version }}",
    "pydantic{{ cookiecutter.pydantic_version }}",
{% if cookiecutter.include_langfuse == "yes" %}
    "langfuse{{ cookiecutter.langfuse_version }}",
{% endif %}
    "typer>=0.15.0",
]
```

### Step 2: app/server.py
**Variables to replace:**
- `name="fastmcp-template"` → `name="{{ cookiecutter.project_name }}"`
- `instructions="..."` → `instructions="{{ cookiecutter.project_description }}"`
- `RefCache(name="fastmcp-template")` → `RefCache(name="{{ cookiecutter.project_slug }}")`

**Conditional tool imports:**
```jinja2
{% if cookiecutter.include_demo_tools == "yes" %}
from app.tools import demo

mcp.tool(demo.hello)
mcp.tool(demo.generate_items)
mcp.tool(demo.store_secret)
mcp.tool(demo.compute_with_secret)
{% endif %}
```

### Step 3: README.md
**Variables to replace:**
- Project name throughout
- `fastmcp-template` → `{{ cookiecutter.project_slug }}`
- Installation commands
- GitHub URLs → `https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}`

**Conditional sections:**
```jinja2
{% if cookiecutter.include_demo_tools == "yes" %}
## Example Tools

The project includes demo tools showing common patterns...
{% endif %}
```

### Step 4: GitHub Actions Workflows
**In `.github/workflows/release.yml`:**
```jinja2
env:
  APP_IMAGE_NAME: {{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}
  BASE_IMAGE_NAME: {{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}-base
  
# Keep GitHub Actions syntax with raw blocks:
- name: Build image
  run: |
    docker build -t {% raw %}${{ env.APP_IMAGE_NAME }}:${{ github.sha }}{% endraw %} .
```

**In `publish.yml`:**
- Package name already comes from pyproject.toml (no change needed)
- But verify trusted publisher setup instructions reference correct repo

### Step 5: docker-compose.yml
```jinja2
services:
  {{ cookiecutter.project_slug }}:
    image: ghcr.io/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}:latest
    container_name: {{ cookiecutter.project_slug }}
```

### Step 6: docker/Dockerfile.base
```jinja2
LABEL org.opencontainers.image.source="https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}"
LABEL org.opencontainers.image.description="{{ cookiecutter.project_description }}"
```

### Step 7: Conditional Demo Tools
**app/tools/demo.py** - Wrap entire file:
```jinja2
{% if cookiecutter.include_demo_tools == "yes" %}
"""Demo tools for FastMCP server."""
# ... entire file content ...
{% endif %}
```

Or better: Keep file, make it empty when not included:
```jinja2
{% if cookiecutter.include_demo_tools == "yes" %}
# ... demo tool code ...
{% else %}
"""Demo tools module (empty - demo tools not included)."""
pass
{% endif %}
```

### Step 8: tests/test_server.py
**Conditional demo tests:**
```jinja2
{% if cookiecutter.include_demo_tools == "yes" %}
def test_hello():
    """Test hello tool."""
    # ... test code ...

def test_generate_items():
    """Test generate_items tool."""
    # ... test code ...
{% endif %}
```

---

## Files Modified

Priority order:

- [x] `pyproject.toml` - Project metadata (CRITICAL) ✅
- [x] `app/server.py` - Server name and conditional imports (CRITICAL) ✅
- [x] `README.md` - Project documentation (HIGH) ✅
- [x] `.github/workflows/release.yml` - Docker builds (HIGH) ✅
- [x] `.github/workflows/publish.yml` - PyPI publishing (HIGH) ✅
- [x] `.github/workflows/ci.yml` - CI pipeline (HIGH) ✅
- [x] `.github/workflows/cd.yml` - CD pipeline (HIGH) ✅
- [x] `docker-compose.yml` - Service names (HIGH) ✅
- [x] `docker/Dockerfile.base` - OCI labels (HIGH) ✅
- [x] `app/__init__.py` - Package metadata (MEDIUM) ✅
- [x] `LICENSE` - Copyright (MEDIUM) ✅
- [x] `CONTRIBUTORS.md` - New file (MEDIUM) ✅
- [x] `.zed/settings.json` - MCP server config (MEDIUM) ✅
- [x] `TOOLS.md` - Project name (LOW) ✅

---

## Testing Strategy

After each file conversion:

1. **Syntax check:**
   ```bash
   # Verify Jinja2 syntax is valid
   python -c "from jinja2 import Template; Template(open('file').read())"
   ```

2. **Test generation:**
   ```bash
   # Generate with defaults
   cookiecutter . --no-input --output-dir /tmp/test-gen
   
   # Verify generated file
   cat /tmp/test-gen/fastmcp-template/pyproject.toml
   ```

3. **Test with custom values:**
   ```bash
   # Test variable substitution
   cookiecutter . --no-input \
     project_name="Test Server" \
     author_name="Test Author" \
     --output-dir /tmp/test-gen2
   ```

4. **Verify generated project works:**
   ```bash
   cd /tmp/test-gen2/test-server
   uv sync
   uv run pytest
   ```

---

## Acceptance Criteria

- [x] All critical files converted to use Jinja2 variables
- [x] GitHub Actions syntax properly escaped with `{% raw %}{% endraw %}`
- [x] Conditional content works (demo tools, Langfuse)
- [x] `cookiecutter . --no-input` generates valid project
- [x] Template variables work in both interactive and non-interactive mode
- [x] No hardcoded "fastmcp-template" strings in template files
- [x] No hardcoded author information in template files
- [x] Docker images use correct names
- [x] GitHub workflows reference correct repository
- [x] LICENSE has template copyright
- [x] New CONTRIBUTORS.md file created

---

## Edge Cases to Handle

### 1. Shell Variables in Dockerfiles
```dockerfile
# Don't confuse with Jinja2!
ENV PATH="${PATH}:/app/bin"  # Keep as-is, not Jinja2
```

### 2. Python f-strings
```python
# Don't confuse with Jinja2!
message = f"Hello {name}"  # Keep as-is, not Jinja2
```

### 3. Nested Jinja2 Blocks
```jinja2
{% if cookiecutter.include_langfuse == "yes" %}
dependencies = [
    "fastmcp>=2.14.0",
{% if cookiecutter.include_demo_tools == "yes" %}
    # Demo tools need extra deps
    "rich>=13.0.0",
{% endif %}
]
{% endif %}
```

### 4. YAML Anchors and GitHub Actions
```yaml
# Be careful with YAML anchors + Jinja2
base: &base
  image: {{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}
  
service:
  <<: *base  # YAML anchor, not Jinja2
```

---

## Notes

- Start with critical files (pyproject.toml, app/server.py)
- Test generation after each major file conversion
- Keep commits small and focused (one file or group of related files)
- Document any tricky escaping decisions

---

## Completion Log

### 2025-01-08 - Task Complete ✅

**Files Converted:**

1. **`pyproject.toml`** - Full Jinja2 templating
   - Project name, description, author info
   - Conditional Langfuse dependency
   - Python version, entry point
   - Ruff and mypy version targets

2. **`app/server.py`** - Conditional imports and content
   - Server name and description
   - Cache namespace
   - Conditional demo tool imports (if `include_demo_tools == "yes"`)
   - Conditional Langfuse/tracing imports (if `include_langfuse == "yes"`)
   - Conditional tool registration

3. **`README.md`** - Complete rewrite
   - Removed old manual setup instructions
   - Project-specific content with template variables
   - Conditional demo tools section
   - All commands use `{{ cookiecutter.project_slug }}`
   - GitHub URLs use `{{ cookiecutter.github_username }}`

4. **GitHub Actions Workflows** - All escaped properly
   - `release.yml` - All `${{ }}` wrapped in `{% raw %}{% endraw %}`
   - `publish.yml` - Escaped GitHub Actions syntax
   - `ci.yml` - Escaped GitHub Actions syntax
   - `cd.yml` - Escaped GitHub Actions syntax
   - Image names use Cookiecutter variables
   - Special handling for `{{version}}` in semver (Jinja2 escaping)

5. **`docker-compose.yml`** - Service names and images
   - Service name uses `{{ cookiecutter.project_slug }}`
   - Image URLs use `{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}`

6. **`docker/Dockerfile.base`** - OCI labels
   - Source URL with GitHub username and project slug
   - Description from project description
   - Authors label with name and email

7. **`app/__init__.py`** - Package metadata
   - `__author__`, `__email__`, `__license__`
   - Package name in version lookup

8. **`LICENSE`** - Copyright
   - Year from `{{ cookiecutter.__year }}`
   - Author from `{{ cookiecutter.author_name }}`

9. **`CONTRIBUTORS.md`** (NEW) - Contributors file
   - Project lead with GitHub username link
   - Email and role
   - Contribution guidelines

10. **`.zed/settings.json`** - MCP server config
    - Context server names use project slug
    - Command args use project slug

11. **`TOOLS.md`** - Documentation header
    - Project name in title and description

12. **`cookiecutter.json`** - Updated defaults
    - Author name: `l4b4r4b4b4`
    - Author email: `lucas.cansino@mail.de`
    - GitHub username: `l4b4r4b4b4`

**Testing Results:**

✅ **Interactive mode works:**
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template
# Prompts for all values
```

✅ **Non-interactive mode works:**
```bash
cookiecutter . --no-input \
  project_name="Weather Data Server" \
  author_name="Jane Smith" \
  github_username="janesmith" \
  include_demo_tools="yes"
# Generates: weather-data-server/
```

✅ **Generated files have correct values:**
- `pyproject.toml` - name: "weather-data-server", author: "Jane Smith"
- `LICENSE` - Copyright (c) 2025 Jane Smith
- `CONTRIBUTORS.md` - Jane Smith (@janesmith)
- `README.md` - Weather Data Server heading
- `docker-compose.yml` - service: weather-data-server
- All GitHub URLs use janesmith/weather-data-server

**Syntax Escaping Strategy:**

GitHub Actions `${{ }}` → `{% raw %}${{ }}{% endraw %}`
Docker Metadata Action `{{version}}` → `{{'{{version}}'}}`
YAML variables `${VAR}` → Keep as-is (not Jinja2)
Python f-strings `f"{var}"` → Keep as-is (not Jinja2)
Shell variables `${VAR}` → Keep as-is (not Jinja2)

**Key Decisions:**

1. **Removed manual setup instructions from README** - No longer needed with Cookiecutter
2. **Added CONTRIBUTORS.md** - Better than just pyproject.toml for recognition
3. **Updated cookiecutter.json defaults** - Use template maintainer's info as defaults
4. **Comprehensive author metadata** - Added to LICENSE, CONTRIBUTORS, app/__init__.py, Docker labels
5. **Conditional content** - Demo tools and Langfuse are truly optional

**Next Steps:**

- Task 04: Create post-generation hooks (post_gen_project.py)
  - Run `uv sync`
  - Run `git init`
  - Print success message with next steps