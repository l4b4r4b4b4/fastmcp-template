# Cookiecutter Template Variables Reference

This document describes all variables defined in `cookiecutter.json` and how they will be used throughout the template.

---

## Core User Prompts (9 variables)

### 1. `project_name`
- **Type:** String
- **Default:** `"FastMCP Template"`
- **Prompt:** `"project_name [FastMCP Template]:"`
- **Description:** Human-readable project name with spaces/capitals allowed
- **Example:** `"Optimization MCP"`, `"Weather Data Server"`
- **Used in:**
  - `app/server.py` - MCP server display name
  - `README.md` - Project title
  - Initial git commit message

### 2. `project_slug`
- **Type:** Computed (Jinja2 expression)
- **Expression:** `{{ cookiecutter.project_name.lower().replace(' ', '-').replace('_', '-') }}`
- **Description:** Lowercase, hyphenated package name (PyPI/npm style)
- **Example:** `"optimization-mcp"`, `"weather-data-server"`
- **Used in:**
  - `pyproject.toml` - `project.name`
  - `pyproject.toml` - CLI entry point name
  - Docker image names
  - Directory/repository name

### 3. `project_description`
- **Type:** String
- **Default:** `"A FastMCP server with RefCache integration"`
- **Description:** One-line summary for package metadata
- **Example:** `"Mathematical optimization server using CVXPY"`
- **Used in:**
  - `pyproject.toml` - `project.description`
  - `README.md` - Project tagline

### 4. `author_name`
- **Type:** String
- **Default:** `"Your Name"`
- **Description:** Full name for package author metadata
- **Example:** `"Luke Smith"`
- **Used in:**
  - `pyproject.toml` - `project.authors[0].name`

### 5. `author_email`
- **Type:** String
- **Default:** `"you@example.com"`
- **Description:** Contact email for package author
- **Example:** `"luke@example.com"`
- **Used in:**
  - `pyproject.toml` - `project.authors[0].email`

### 6. `python_version`
- **Type:** String
- **Default:** `"3.12"`
- **Description:** Minimum required Python version
- **Example:** `"3.12"`, `"3.13"`
- **Used in:**
  - `pyproject.toml` - `project.requires-python`
  - `docker/Dockerfile.base` - Base image tag

### 7. `include_demo_tools`
- **Type:** Choice (array)
- **Options:** `["no", "yes"]`
- **Default:** `"no"` (first item)
- **Description:** Whether to include demo tools in generated project
- **Used in:**
  - Conditional inclusion of `app/tools/demo.py`
  - Conditional inclusion of demo tests in `tests/test_server.py`
  - Conditional tool registration in `app/server.py`

### 8. `include_langfuse`
- **Type:** Choice (array)
- **Options:** `["yes", "no"]`
- **Default:** `"yes"` (first item)
- **Description:** Whether to include Langfuse tracing integration
- **Used in:**
  - `pyproject.toml` - Include `langfuse>=3.10.0` in dependencies
  - `app/server.py` - Conditional Langfuse initialization

### 9. `github_username`
- **Type:** String
- **Default:** `"yourusername"`
- **Description:** GitHub username or organization for Docker images and URLs
- **Example:** `"l4b4r4b4b4"`, `"myorg"`
- **Used in:**
  - `docker-compose.yml` - Image names
  - `.github/workflows/release.yml` - GHCR push targets
  - `docker/Dockerfile.base` - OCI labels

---

## Dependency Versions (4 variables)

These are NOT prompted - they're constants that match the current template's pyproject.toml.

### 10. `fastmcp_version`
- **Value:** `">=2.14.0"`
- **Used in:** `pyproject.toml` dependencies

### 11. `mcp_refcache_version`
- **Value:** `">=0.1.0"`
- **Used in:** `pyproject.toml` dependencies

### 12. `langfuse_version`
- **Value:** `">=3.10.0"`
- **Used in:** `pyproject.toml` dependencies (if `include_langfuse == "yes"`)

### 13. `pydantic_version`
- **Value:** `">=2.10.0"`
- **Used in:** `pyproject.toml` dependencies

---

## Private/Computed Variables (4 variables)

These start with `__` and are NOT prompted - they're computed from other variables.

### 14. `__project_slug_underscore`
- **Expression:** `{{ cookiecutter.project_slug.replace('-', '_') }}`
- **Description:** Python module name (hyphens → underscores)
- **Example:** `"optimization_mcp"`, `"weather_data_server"`
- **Used in:**
  - `pyproject.toml` - `project.scripts` entry point (app package import)
  - Python import statements (if needed)

### 15. `__docker_image`
- **Expression:** `{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}`
- **Description:** Full Docker image name (without tag)
- **Example:** `"l4b4r4b4b4/optimization-mcp"`
- **Used in:**
  - `docker-compose.yml` - Image references
  - `.github/workflows/release.yml` - Build and push targets

### 16. `__year`
- **Value:** `"2025"`
- **Description:** Current year for copyright notices
- **Used in:**
  - `LICENSE` - Copyright year
  - Code file headers (if added in future)

### 17. (Reserved) `__cache_namespace`
- **Expression:** `{{ cookiecutter.project_slug }}`
- **Description:** Default cache namespace for RefCache
- **Example:** `"optimization-mcp"`
- **Potential use in:**
  - `app/server.py` - RefCache initialization

---

## Variable Dependencies

```
project_name
    ↓
project_slug ────────────┬──────────────┐
    ↓                    ↓              ↓
__project_slug_underscore  github_username  __year
                              ↓
                          __docker_image
```

---

## Jinja2 Template Usage Examples

### In `pyproject.toml`:
```toml
[project]
name = "{{ cookiecutter.project_slug }}"
version = "0.0.0"
description = "{{ cookiecutter.project_description }}"
authors = [
    { name = "{{ cookiecutter.author_name }}", email = "{{ cookiecutter.author_email }}" }
]
requires-python = ">={{ cookiecutter.python_version }}"
dependencies = [
    "fastmcp{{ cookiecutter.fastmcp_version }}",
    "mcp-refcache{{ cookiecutter.mcp_refcache_version }}",
{% if cookiecutter.include_langfuse == "yes" %}
    "langfuse{{ cookiecutter.langfuse_version }}",
{% endif %}
]

[project.scripts]
{{ cookiecutter.project_slug }} = "app.__main__:app"
```

### In `app/server.py`:
```python
mcp = FastMCP(
    name="{{ cookiecutter.project_name }}",
    instructions="{{ cookiecutter.project_description }}",
)

_cache = RefCache(
    name="{{ cookiecutter.project_slug }}",
    # ...
)

{% if cookiecutter.include_demo_tools == "yes" %}
from app.tools import hello, generate_items

mcp.tool(hello)
mcp.tool(generate_items)
{% endif %}
```

### In `docker-compose.yml`:
```yaml
services:
  {{ cookiecutter.project_slug }}:
    image: ghcr.io/{{ cookiecutter.__docker_image }}:latest
```

---

## Validation Rules (Future: pre_gen_project.py)

Potential validations to add in hooks:
- `project_slug` must match `^[a-z0-9-]+$` (lowercase, numbers, hyphens only)
- `author_email` must match email regex
- `github_username` must not contain spaces or special chars
- `python_version` must be >= 3.12

---

## Testing Scenarios

### Scenario 1: Minimal Project (No Demo Tools)
```
project_name: Weather API
project_slug: weather-api (computed)
include_demo_tools: no
include_langfuse: yes
```
Result: Clean project, no demo files, Langfuse included

### Scenario 2: Learning Project (With Demo Tools)
```
project_name: My First MCP
project_slug: my-first-mcp (computed)
include_demo_tools: yes
include_langfuse: no
```
Result: Demo tools included for reference, no Langfuse

### Scenario 3: Production Project
```
project_name: ACME Corp Data API
project_slug: acme-corp-data-api (computed)
include_demo_tools: no
include_langfuse: yes
github_username: acme-corp
```
Result: Clean, production-ready with observability

---

## Notes

- All computed variables use Jinja2 filters (`.lower()`, `.replace()`)
- Choice variables default to first item in array
- Private variables (`__*`) won't appear in prompts
- Dependency versions should be updated as template evolves