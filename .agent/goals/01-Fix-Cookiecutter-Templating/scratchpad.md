# Goal 01: Fix Cookiecutter Templating Issues

## Status: 🟢 Complete

**Created:** 2025-01-08
**Updated:** 2025-01-08
**Completed:** 2025-01-08
**Priority:** High

---

## Objective

Fix hardcoded values in template files that should use cookiecutter template variables. Currently, **70 references** across **20 files** have hardcoded `fastmcp-template`, `FastMCP Template`, or `l4b4r4b4b4` instead of using the cookiecutter variables defined in `cookiecutter.json`.

---

## Problem Description

During the cookiecutter conversion (archived Goal A02), many files were not fully templated. When users generate a project from this template, they'll end up with hardcoded references that don't match their project settings.

### Available Cookiecutter Variables

From `cookiecutter.json`:
- `{{ cookiecutter.project_name }}` - Human-readable project name (e.g., "My MCP Server")
- `{{ cookiecutter.project_slug }}` - Kebab-case identifier (e.g., "my-mcp-server")
- `{{ cookiecutter.project_description }}` - Project description
- `{{ cookiecutter.github_username }}` - GitHub username/org
- `{{ cookiecutter.author_name }}` / `{{ cookiecutter.author_email }}`
- `{{ cookiecutter.__project_slug_underscore }}` - Snake_case version (e.g., "my_mcp_server")
- `{{ cookiecutter.__docker_image }}` - Pre-computed `github_username/project_slug`

---

## Current Inventory (Verified via grep)

### Summary by Category

| Category | Files | References |
|----------|-------|------------|
| GitHub Workflows | 4 | 18 |
| App Source Files | 7 | 16 |
| Test Files | 3 | 8 |
| Documentation Files | 4 | 24 |
| Config Files | 1 | 1 |
| **Total** | **20** | **70** |

Note: `README.md` is already properly templated (excluded from count).

---

## Files Requiring Changes (20 files, 70 references)

### GitHub Workflows (4 files, 18 references)

#### `.github/workflows/publish.yml` (7 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 8 | `pypi.org/manage/project/fastmcp-template/` | `pypi.org/manage/project/{{ cookiecutter.project_slug }}/` |
| 10 | `Owner: l4b4r4b4b4` | `Owner: {{ cookiecutter.github_username }}` |
| 11 | `Repository: fastmcp-template` | `Repository: {{ cookiecutter.project_slug }}` |
| 16 | `uvx fastmcp-template stdio` | `uvx {{ cookiecutter.project_slug }} stdio` |
| 17 | `uvx fastmcp-template sse` | `uvx {{ cookiecutter.project_slug }} sse` |
| 18 | `uvx fastmcp-template streamable-http` | `uvx {{ cookiecutter.project_slug }} streamable-http` |
| 75 | `url: https://pypi.org/project/fastmcp-template` | `url: https://pypi.org/project/{{ cookiecutter.project_slug }}` |

#### `.github/workflows/cd.yml` (6 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `# CD Pipeline for FastMCP Template` | `# CD Pipeline for {{ cookiecutter.project_name }}` |
| 70 | `IMAGE_NAME: .../fastmcp-template` | `IMAGE_NAME: .../{{ cookiecutter.project_slug }}` |
| 123 | `cd /opt/fastmcp-template` | `cd /opt/{{ cookiecutter.project_slug }}` |
| 143 | `deployment/fastmcp-template` | `deployment/{{ cookiecutter.project_slug }}` |
| 144 | `fastmcp-template=...` | `{{ cookiecutter.project_slug }}=...` |
| 146 | `deployment/fastmcp-template -n fastmcp` | `deployment/{{ cookiecutter.project_slug }} -n {{ cookiecutter.project_slug }}` |

#### `.github/workflows/ci.yml` (1 reference)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `# CI Pipeline for FastMCP Template` | `# CI Pipeline for {{ cookiecutter.project_name }}` |

#### `.github/copilot-instructions.md` (1 reference)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `# GitHub Copilot Instructions for fastmcp-template` | `# GitHub Copilot Instructions for {{ cookiecutter.project_slug }}` |

---

### App Source Files (7 files, 16 references)

#### `app/__main__.py` (7 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `CLI entry point for FastMCP Template Server` | `CLI entry point for {{ cookiecutter.project_name }}` |
| 4-6 | `uvx fastmcp-template ...` (3 occurrences) | `uvx {{ cookiecutter.project_slug }} ...` |
| 23 | `name="fastmcp-template"` | `name="{{ cookiecutter.project_slug }}"` |
| 24 | `help="FastMCP Template Server..."` | `help="{{ cookiecutter.project_description }}"` |
| 164 | `"""FastMCP Template Server...` | `"""{{ cookiecutter.project_name }}...` |
| 172 | `typer.echo(f"fastmcp-template {__version__}")` | `typer.echo(f"{{ cookiecutter.project_slug }} {__version__}")` |

#### `app/config.py` (2 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Configuration module for FastMCP Template Server` | `Configuration module for {{ cookiecutter.project_name }}` |
| 35 | `"fastmcp-template" / "cache.db"` | `"{{ cookiecutter.project_slug }}" / "cache.db"` |

#### `app/tracing.py` (1 reference)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Langfuse tracing integration for FastMCP Template` | `Langfuse tracing integration for {{ cookiecutter.project_name }}` |

#### `app/tools/__init__.py` (1 reference)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Tools module for FastMCP Template Server` | `Tools module for {{ cookiecutter.project_name }}` |

#### `app/tools/demo.py` (2 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Demo tools for FastMCP Template Server` | `Demo tools for {{ cookiecutter.project_name }}` |
| 46 | `"server": "fastmcp-template"` | `"server": "{{ cookiecutter.project_slug }}"` |

#### `app/tools/health.py` (2 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Health check tools for FastMCP Template Server` | `Health check tools for {{ cookiecutter.project_name }}` |
| 36 | `"server": "fastmcp-template"` | `"server": "{{ cookiecutter.project_slug }}"` |

#### `app/prompts/__init__.py` (2 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Prompts module for FastMCP Template Server` | `Prompts module for {{ cookiecutter.project_name }}` |
| 11 | `# FastMCP Template Guide` | `# {{ cookiecutter.project_name }} Guide` |

---

### Test Files (3 files, 8 references)

#### `tests/__init__.py` (1 reference)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Tests for fastmcp-template MCP server` | `Tests for {{ cookiecutter.project_slug }} MCP server` |

#### `tests/conftest.py` (1 reference)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Pytest configuration and fixtures for fastmcp-template` | `Pytest configuration and fixtures for {{ cookiecutter.project_slug }}` |

#### `tests/test_server.py` (6 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `Tests for the fastmcp-template server module` | `Tests for the {{ cookiecutter.project_slug }} server module` |
| 25 | `assert mcp.name == "FastMCP Template"` | `assert mcp.name == "{{ cookiecutter.project_name }}"` |
| 30 | `assert cache.name == "fastmcp-template"` | `assert cache.name == "{{ cookiecutter.project_slug }}"` |
| 49 | `assert result["server"] == "fastmcp-template"` | `assert result["server"] == "{{ cookiecutter.project_slug }}"` |
| 257 | `assert result["server"] == "fastmcp-template"` | `assert result["server"] == "{{ cookiecutter.project_slug }}"` |
| 264 | `assert result["cache"] == "fastmcp-template"` | `assert result["cache"] == "{{ cookiecutter.project_slug }}"` |

---

### Documentation Files (4 files, 24 references)

#### `docs/README.md` (14 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `# FastMCP Template Documentation` | `# {{ cookiecutter.project_name }} Documentation` |
| 3 | `FastMCP Template project` | `{{ cookiecutter.project_name }} project` |
| 221 | `uv run fastmcp-template` | `uv run {{ cookiecutter.project_slug }}` |
| 224 | `uv run fastmcp-template --transport...` | `uv run {{ cookiecutter.project_slug }} --transport...` |
| 236-237 | `fastmcp-template` | `{{ cookiecutter.project_slug }}` |
| 255 | `fastmcp-template:latest` | `{{ cookiecutter.project_slug }}:latest` |
| 258 | `fastmcp-template:dev` | `{{ cookiecutter.project_slug }}:dev` |
| 265 | `fastmcp-template:latest` | `{{ cookiecutter.project_slug }}:latest` |
| 271 | `fastmcp-template:latest` | `{{ cookiecutter.project_slug }}:latest` |
| 274 | `fastmcp-template:dev` | `{{ cookiecutter.project_slug }}:dev` |
| 295 | `ghcr.io/l4b4r4b4b4/fastmcp-base` | `ghcr.io/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}-base` |
| 311-312 | `ghcr.io/l4b4r4b4b4/fastmcp-*` | `ghcr.io/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}*` |

#### `CHANGELOG.md` (6 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 35 | `uvx fastmcp-template stdio` | `uvx {{ cookiecutter.project_slug }} stdio` |
| 41 | `Initial release of FastMCP Template` | `Initial release of {{ cookiecutter.project_name }}` |
| 69 | `github.com/l4b4r4b4b4/fastmcp-template/compare/...` | `github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/compare/...` |
| 70-72 | `github.com/l4b4r4b4b4/fastmcp-template/releases/...` | `github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/releases/...` |

#### `CONTRIBUTING.md` (4 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `# Contributing to fastmcp-template` | `# Contributing to {{ cookiecutter.project_slug }}` |
| 3 | `contributing to fastmcp-template!` | `contributing to {{ cookiecutter.project_slug }}!` |
| 17 | `git clone https://github.com/l4b4r4b4b4/fastmcp-template` | `git clone https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}` |
| 18 | `cd fastmcp-template` | `cd {{ cookiecutter.project_slug }}` |

#### `TOOLS.md` (4 references)
| Line | Current | Should Be |
|------|---------|-----------|
| 35 | `"server": "fastmcp-template"` | `"server": "{{ cookiecutter.project_slug }}"` |
| 42 | `"server": "fastmcp-template"` | `"server": "{{ cookiecutter.project_slug }}"` |
| 190 | `"server": "fastmcp-template"` | `"server": "{{ cookiecutter.project_slug }}"` |
| 191 | `"cache": "fastmcp-template"` | `"cache": "{{ cookiecutter.project_slug }}"` |

---

### Config Files (1 file, 1 reference)

#### `.pre-commit-config.yaml` (1 reference)
| Line | Current | Should Be |
|------|---------|-----------|
| 1 | `# Pre-commit hooks for fastmcp-template` | `# Pre-commit hooks for {{ cookiecutter.project_slug }}` |

---

## External References to Preserve

These are references to external libraries and should NOT be changed:
- `github.com/l4b4r4b4b4/mcp-refcache` (mcp-refcache library repo)
- `github.com/jlowin/fastmcp` (FastMCP library repo)
- `mcp_refcache` (Python import - external library)

---

## Implementation Plan

### Task 01: Fix GitHub Workflow Files (4 files) ✅ COMPLETE
- [x] `.github/workflows/publish.yml` - PyPI URLs, owner, repository, usage examples
- [x] `.github/workflows/cd.yml` - Pipeline title, image name, deployment references
- [x] `.github/workflows/ci.yml` - Pipeline title
- [x] `.github/copilot-instructions.md` - Header

### Task 02: Fix App Source Files (7 files) ✅ COMPLETE
- [x] `app/__main__.py` - CLI name, help, version, docstrings, usage examples
- [x] `app/config.py` - Docstring, SQLite cache path
- [x] `app/tracing.py` - Docstring
- [x] `app/tools/__init__.py` - Docstring
- [x] `app/tools/demo.py` - Docstring, server name in response
- [x] `app/tools/health.py` - Docstring, server name in response
- [x] `app/prompts/__init__.py` - Docstring, prompt header

### Task 03: Fix Test Files (3 files) ✅ COMPLETE
- [x] `tests/__init__.py` - Docstring
- [x] `tests/conftest.py` - Docstring
- [x] `tests/test_server.py` - Docstring, assertion values (6 assertions)

### Task 04: Fix Documentation Files (4 files) ✅ COMPLETE
- [x] `docs/README.md` - Title, references, Docker image names (14 references)
- [x] `CHANGELOG.md` - References and GitHub URLs
- [x] `CONTRIBUTING.md` - Title, intro, git clone URL
- [x] `TOOLS.md` - Server/cache names in examples

### Task 05: Fix Config Files (1 file) ✅ COMPLETE
- [x] `.pre-commit-config.yaml` - Header comment

### Task 06: Final Verification ✅ COMPLETE
- [x] Run `cookiecutter . --no-input project_name="Test Project" github_username="testuser"`
- [x] Grep generated project for any remaining hardcoded values
- [x] Run tests on generated project
- [x] Verify all 20 files have correct values

**Verification Results:**
- Generated test project successfully with `project_name="Test Project"` and `github_username="testuser"`
- **0 hardcoded references** found in generated project (grep returned no matches)
- All generated files contain correct project-specific values:
  - CLI name: `test-project`
  - Project name: `Test Project`
  - GitHub username: `testuser`
  - Server responses: `"server": "test-project"`
  - Cache name: `"cache": "test-project"`
- **All 101 tests pass** with demo tools enabled
- Fixed 2 additional Docker files discovered during verification:
  - `docker/Dockerfile` - Title, comments, base image (4 references)
  - `docker/Dockerfile.dev` - Title, labels, CMD (5 references)

---

## Acceptance Criteria ✅ ALL MET

- [x] All 22 files updated with proper cookiecutter variables (79 references total)
  - Original 20 files: 70 references ✅
  - Additional 2 Docker files: 9 references ✅
- [x] No remaining hardcoded `fastmcp-template` in template files (except external lib references)
- [x] No remaining hardcoded `l4b4r4b4b4` in template files (except external lib references)
- [x] No remaining hardcoded `FastMCP Template` in template files
- [x] Generated projects have correct, project-specific values
- [x] Tests pass on generated projects (101/101 tests pass)
- [x] External library references to `mcp-refcache` preserved as-is

---

## Notes

### Escaping Rules
- **GitHub Actions `${{ }}`** - Already escaped with `{% raw %}{% endraw %}` in existing files
- **Cookiecutter `{{ }}`** - Must NOT be escaped (rendered at generation time)
- **Jinja blocks** - Already using `{% if %}` / `{% endif %}` correctly

### Variable Usage Patterns
- `{{ cookiecutter.project_name }}` - Human-readable names, titles, descriptions
- `{{ cookiecutter.project_slug }}` - CLI commands, package names, URLs, file paths
- `{{ cookiecutter.github_username }}` - GitHub URLs, Docker image registry paths
- `{{ cookiecutter.__docker_image }}` - Pre-computed `github_username/project_slug`

---

## Proposed Approach

**Strategy**: Fix files in batches by category for easier review and testing.

1. **GitHub Workflows** - Fix all 4 workflow files together (highest impact on CI/CD)
2. **App Source Files** - Fix all 7 Python source files (core functionality)
3. **Test Files** - Fix all 3 test files (assertions must match source)
4. **Documentation** - Fix all 4 markdown docs (user-facing)
5. **Config** - Fix 1 config file (trivial)
6. **Verify** - Generate test project and validate

**Risk Mitigation**:
- Each batch can be tested independently
- Tests should pass after each batch (source + tests together)
- Final verification catches any missed references

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-08 | Created as Goal 03 | Discovered during review of cd.yml |
| 2025-01-08 | Expanded scope to 21 files | Comprehensive grep found 74 references |
| 2025-01-08 | Preserve mcp-refcache references | External library, not project-specific |
| 2025-01-08 | Renumbered to Goal 01 | Goals 01-02 archived, this is now top priority |
| 2025-01-08 | Refined count to 20 files, 70 refs | README.md already templated; verified via grep |
| 2025-01-08 | Completed all 6 tasks | Found 2 additional Docker files during verification (22 files, 79 refs total) |
| 2025-01-08 | Verification: 0 hardcoded refs, 101 tests pass | Generated test project validates all changes work correctly |