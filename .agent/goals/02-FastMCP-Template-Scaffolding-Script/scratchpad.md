W# Goal 02: Convert FastMCP Template to Cookiecutter Format

**Status:** 🟡 In Progress
**Priority:** High
**Created:** 2025-01-08
**Last Updated:** 2025-01-08

---

## Overview

Convert the fastmcp-template repository to Cookiecutter format to automate project generation and customization. This eliminates repetitive manual steps by using the battle-tested Cookiecutter tool (5M downloads/month) instead of building custom scaffolding. Users answer prompts, Cookiecutter generates a clean project with demo tools optionally excluded at generation time.

**Key Decision:** After researching existing solutions (Cookiecutter, Copier, Cruft, PyScaffold), we chose Cookiecutter because our needs are simple templating, not complex code transformation.

---

## Problem Statement

When starting a new MCP server project from fastmcp-template:

**Current Manual Process:**
1. Clone or copy the template repository
2. Remove demo tools (`hello`, `generate_items`, `store_secret`, `compute_with_secret`)
3. Update `app/server.py` with new server name and instructions
4. Clean up `app/prompts/__init__.py` to remove demo references
5. Remove demo tool tests from `tests/test_server.py`
6. Update `pyproject.toml` with new project name, description, dependencies
7. Update `README.md` with project-specific information
8. Remove template-specific documentation
9. Initialize git repository (optional)
10. Run initial tests to verify cleanup

**Pain Points:**
- 10+ manual steps, each error-prone
- Easy to miss cleanup steps (orphaned tests, outdated docs)
- Inconsistent starting state across projects
- Time-consuming (15-30 minutes per new project)
- Requires remembering all the locations that need updating

---

## Objectives

### Primary Goals
1. **Use Existing Tools** - Leverage Cookiecutter instead of reinventing
2. **Template Variables** - Project name, description, author via Jinja2
3. **Conditional Inclusion** - Demo tools optional (`include_demo_tools`)
4. **Post-Generation Automation** - Run `uv sync`, `git init` via hooks
5. **Fast Setup** - Reduce setup time from 30 minutes to 1-2 minutes

### Success Criteria
- [ ] Script executes in <30 seconds
- [ ] Generated project passes all tests (no demo tool references)
- [ ] Generated project passes linting (ruff check + format)
- [ ] README and documentation reflect new project name
- [ ] pyproject.toml configured with new project metadata
- [ ] Demo tools and tests completely removed
- [ ] Server instructions updated with generic starter text
- [ ] Git repository optionally initialized
- [ ] Script has comprehensive error handling
- [ ] Script provides clear user feedback during execution

---

## User Experience

### Desired Usage

```bash
# Install Cookiecutter (one-time)
uv tool install cookiecutter
# or
pipx install cookiecutter

# Create new project from template
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# Interactive prompts:
# project_name [FastMCP Template]: Optimization MCP
# project_slug [optimization-mcp]: <press Enter>
# project_description: Mathematical optimization server using CVXPY
# author_name [Your Name]: Luke Smith
# author_email [you@example.com]: luke@example.com
# python_version [3.12]: <press Enter>
# include_demo_tools [no]: <press Enter>
# include_langfuse [yes]: <press Enter>
# github_username [yourusername]: l4b4r4b4b4

# Cookiecutter generates project and runs post-gen hook:
# ✓ Created project directory: ./optimization-mcp
# ✓ Rendered all templates with your values
# ✓ Excluded demo tools (include_demo_tools=no)
# ✓ Running post-generation hooks...
# ✓ Installed dependencies with uv sync
# ✓ Initialized git repository
# ✓ Created initial commit
#
# Next steps:
#   cd optimization-mcp
#   uv run pytest
#   uv run optimization-mcp stdio
#
# Your FastMCP server is ready! 🚀
```

### Example: With Demo Tools

```bash
# If you want to keep demo tools for reference:
cookiecutter gh:l4b4r4b4b4/fastmcp-template

# When prompted:
# include_demo_tools [no]: yes

# Generated project will include:
# - app/tools/demo.py (hello, generate_items)
# - Demo tool tests
# - Demo examples in prompts
```

---

## Technical Design

### Cookiecutter Template Structure

```
fastmcp-template/                    # Repository root
├── cookiecutter.json                # Template configuration & prompts
├── hooks/                           # Pre/post generation scripts
│   ├── pre_gen_project.py          # Validation before generation
│   └── post_gen_project.py         # Run uv sync, git init, cleanup
├── {{cookiecutter.project_slug}}/   # Template directory (gets copied)
│   ├── .agent/
│   │   └── goals/
│   │       └── 00-Template-Goal/   # Only template goal (not our dev goals)
│   ├── app/
│   │   ├── server.py               # Uses {{ cookiecutter.project_name }}
│   │   ├── __init__.py
│   │   └── tools/
│   │       ├── __init__.py
│   │       {% if cookiecutter.include_demo_tools == 'yes' %}
│   │       ├── demo.py             # Conditionally included
│   │       {% endif %}
│   │       ├── cache.py
│   │       ├── context.py
│   │       └── secrets.py
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_server.py          # Demo tests conditionally included
│   ├── docker/
│   ├── .github/workflows/
│   ├── pyproject.toml               # Templated with variables
│   ├── README.md                    # Project-specific content
│   └── ...
└── .agent/                          # Our development (NOT copied!)
    ├── scratchpad.md
    └── goals/
        ├── 01-*/
        ├── 02-*/                    # This goal
        └── scratchpad.md
```

### Cookiecutter Configuration

**cookiecutter.json:**
```json
{
  "project_name": "FastMCP Template",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
  "project_description": "A FastMCP server with RefCache integration",
  "author_name": "Your Name",
  "author_email": "you@example.com",
  "python_version": "3.12",
  "include_demo_tools": ["no", "yes"],
  "include_langfuse": ["yes", "no"],
  "github_username": "yourusername"
}
```

### Post-Generation Hook

**hooks/post_gen_project.py:**
```python
#!/usr/bin/env python
"""Post-generation hook to set up the project."""
import subprocess
import sys
from pathlib import Path

def main():
    project_root = Path.cwd()

    print("🔧 Running post-generation setup...")

    # Install dependencies
    print("📦 Installing dependencies with uv...")
    subprocess.run(["uv", "sync"], check=True)

    # Initialize git
    print("🔀 Initializing git repository...")
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run([
        "git", "commit", "-m",
        "Initial commit from fastmcp-template"
    ], check=True)

    print("✅ Project setup complete!")
    print(f"\nNext steps:")
    print(f"  cd {project_root.name}")
    print(f"  uv run pytest")
    print(f"  uv run {project_root.name} stdio")

if __name__ == "__main__":
    main()
```

---

## Implementation Tasks

### Task 01: Create cookiecutter.json Configuration
**Goal:** Define template variables and prompts

**Subtasks:**
- [ ] Create `cookiecutter.json` at repository root
- [ ] Define all template variables (project_name, slug, description, etc.)
- [ ] Set sensible defaults
- [ ] Add validation rules (if needed)
- [ ] Test locally with `cookiecutter .`

**Template Variables:**
- project_name (display name)
- project_slug (auto-generated from name)
- project_description
- author_name, author_email
- python_version
- include_demo_tools (yes/no)
- include_langfuse (yes/no)
- github_username

**Estimated Effort:** 1 hour

---

### Task 02: Restructure Repository for Cookiecutter
**Goal:** Move current content into template directory

**Subtasks:**
- [ ] Create `{{cookiecutter.project_slug}}/` directory
- [ ] Move all app code into template directory
- [ ] Keep `.agent/goals/01-*`, `02-*`, etc. at root (our dev goals)
- [ ] Copy `.agent/goals/00-Template-Goal/` into template (for users)
- [ ] Update `.gitignore` if needed
- [ ] Verify structure matches Cookiecutter pattern

**Directory Structure After:**
```
fastmcp-template/
├── cookiecutter.json
├── hooks/
├── {{cookiecutter.project_slug}}/  # User's project
│   ├── .agent/
│   │   └── goals/
│   │       └── 00-Template-Goal/
│   ├── app/
│   ├── tests/
│   └── ...
└── .agent/                          # Our development
    └── goals/
        ├── 01-*/
        └── 02-*/
```

**Estimated Effort:** 1 hour

---

### Task 03: Convert Files to Jinja2 Templates
**Goal:** Add template variables to all project files

**Subtasks:**
- [ ] Add `{% if cookiecutter.include_demo_tools == 'yes' %}` blocks
- [ ] Wrap demo tool imports in conditionals
- [ ] Wrap demo tool registration in conditionals
- [ ] Conditionally include `app/tools/demo.py` file
- [ ] Conditionally include demo tests in `test_server.py`
- [ ] Update `app/tools/__init__.py` exports conditionally
- [ ] Test both with and without demos
- [ ] Verify clean output when demos excluded

**Files to update:**
- app/server.py (imports, tool registration)
- app/tools/__init__.py (exports)
- app/tools/demo.py (entire file conditional)
- tests/test_server.py (demo test classes)
- app/prompts/__init__.py (demo examples)

**Jinja2 patterns:**
```python
{% if cookiecutter.include_demo_tools == 'yes' %}
from app.tools import hello, generate_items
{% endif %}

{% if cookiecutter.include_demo_tools == 'yes' %}
mcp.tool(hello)
{% endif %}
```

**Estimated Effort:** 2-3 hours

---
</text>

<old_text line=260>
### Task 04: Template Generation
**Goal:** Jinja2 templating for all project files

**Subtasks:**
- [ ] Set up Jinja2 environment
- [ ] Create template context from user input
- [ ] Render all project files with substitutions
- [ ] Handle conditional file inclusion
- [ ] Special handling for binary files (keep as-is)
- [ ] Write tests for template rendering

**Template Variables:**
```python
{
    "project_name": "Optimization MCP",
    "project_slug": "optimization-mcp",
    "project_description": "...",
    "author_name": "Luke Smith",
    "author_email": "luke@example.com",
    "python_version": "3.12",
    "include_demos": False,
    "include_langfuse": True,
    "github_username": "l4b4r4b4b4",
    "year": 2025,
}
```

**Files to Template:**
- pyproject.toml
- app/server.py
- app/__init__.py
- README.md
- docker-compose.yml
- docker/Dockerfile.base
- .github/workflows/*.yml

**Estimated Effort:** 3-4 hours

---

### Task 04: Template Generation
**Goal:** Generate project-specific files from templates

**Subtasks:**
- [ ] Create Jinja2 templates for:
  - `app/server.py` (minimal server)
  - `README.md` (project-specific)
  - `app/prompts/__init__.py` (starter prompts)
  - Optional: `app/tools/example.py` (tool template)
- [ ] Implement template rendering with context
- [ ] Add template validation
- [ ] Write tests for template generation

**Template Variables:**
- `project_name` - Python package name
- `project_title` - Display name
- `project_description` - Short description
- `author_name` - Author name
- `author_email` - Author email
- `server_type` - stdio | http | both
- `year` - Current year (for copyright)

**Example Template (`server.py.jinja`):**
```python
"""{{ project_title }} - {{ project_description }}"""

from fastmcp import FastMCP
from mcp_refcache import RefCache

mcp = FastMCP(
    name="{{ project_title }}",
    instructions="""{{ project_description }}

Add your tool descriptions here.
"""
)

cache = RefCache(
    name="{{ project_name }}",
    default_ttl=3600,
)

# Add your tools here

if __name__ == "__main__":
    mcp.run()
```

**Estimated Effort:** 3-4 hours

---

### Task 05: Project Metadata Updates
**Goal:** Update pyproject.toml and other metadata files

**Subtasks:**
- [ ] Parse `pyproject.toml` with `tomli`/`tomli-w`
- [ ] Update project name, description, version
- [ ] Update author information
- [ ] Clean up template-specific dependencies
- [ ] Update entry points (CLI commands)
- [ ] Write tests for metadata updates

**Key Updates:**
```toml
[project]
name = "my-mcp-server"
description = "My awesome MCP server"
authors = [{name = "Your Name", email = "you@example.com"}]
version = "0.0.0"

[project.scripts]
my-mcp-server = "app.__main__:run"
```

**Estimated Effort:** 2 hours

---

### Task 06: Git Integration
**Goal:** Optional git repository initialization

**Subtasks:**
- [ ] Check for existing git repository
- [ ] Initialize git repository (if requested)
- [ ] Create initial commit with clean template
- [ ] Add sensible `.gitignore` (if not present)
- [ ] Optionally set remote origin
- [ ] Write tests for git operations

**Git Operations:**
```python
def init_git_repo(project_path: Path) -> None
def create_initial_commit(project_path: Path, message: str) -> None
def add_remote(project_path: Path, remote_url: str) -> None
```

**Estimated Effort:** 1-2 hours

---

### Task 07: Dependency Management
**Goal:** Install dependencies after scaffolding

**Subtasks:**
- [ ] Detect package manager (uv, pip, poetry)
- [ ] Run dependency installation (if requested)
- [ ] Verify installation success
- [ ] Handle installation errors gracefully
- [ ] Write tests for dependency operations

**Package Manager Detection:**
```python
def detect_package_manager() -> str:
    # Check for uv, poetry, pip in order

def install_dependencies(project_path: Path, package_manager: str) -> None:
    # Run appropriate install command
```

**Estimated Effort:** 1-2 hours

---

### Task 08: Post-Scaffold Verification
**Goal:** Verify scaffolded project is valid

**Subtasks:**
- [ ] Run linting (ruff check)
- [ ] Run formatting (ruff format)
- [ ] Run tests (pytest)
- [ ] Check for remaining template markers
- [ ] Generate verification report
- [ ] Write tests for verification

**Verification Checks:**
```python
def verify_project(project_path: Path) -> VerificationReport:
    - Check linting passes
    - Check tests pass
    - Check no demo tool references remain
    - Check README is updated
    - Check pyproject.toml is valid
```

**Estimated Effort:** 2-3 hours

---

### Task 09: Documentation & Examples
**Goal:** Comprehensive documentation for the script

**Subtasks:**
- [ ] Write main README with usage examples
- [ ] Document all CLI options
- [ ] Create troubleshooting guide
- [ ] Add contribution guidelines
- [ ] Create demo video/GIF (optional)
- [ ] Write FAQ

**Documentation Sections:**
- Installation
- Quick Start
- CLI Reference
- Configuration Options
- Troubleshooting
- Development Guide

**Estimated Effort:** 2-3 hours

---

### Task 10: Testing & Publishing
**Goal:** Comprehensive tests and PyPI publication

**Subtasks:**
- [ ] Write integration tests (full scaffold cycle)
- [ ] Test with different configurations
- [ ] Test error handling and rollback
- [ ] Test on clean clone of fastmcp-template
- [ ] Set up CI/CD (GitHub Actions)
- [ ] Publish to PyPI (version 0.1.0)
- [ ] Create GitHub release

**Test Coverage Goals:**
- Unit tests: 80%+ coverage
- Integration tests: All user flows
- Error scenarios: All rollback paths

**Estimated Effort:** 3-4 hours

---

## Technical Decisions & Tradeoffs

### Decision 1: AST vs Regex for Code Manipulation
**Choice:** Use Python `ast` module for parsing and modifying Python files

**Rationale:**
- ✅ Type-safe, preserves code structure
- ✅ Handles edge cases (nested functions, decorators)
- ✅ Can regenerate formatted code
- ✅ Less error-prone than regex
- ❌ More complex implementation
- ❌ Requires Python 3.9+ for some features

**Alternatives:**
- Regex: ❌ Fragile, misses edge cases
- Manual templates: ❌ Loses existing structure

---

### Decision 2: Typer vs Click vs Argparse
**Choice:** Use Typer for CLI framework

**Rationale:**
- ✅ Modern, type-safe CLI framework
- ✅ Beautiful output with Rich integration
- ✅ Automatic help generation
- ✅ Interactive prompts built-in
- ❌ Additional dependency

**Alternatives:**
- Click: ❌ Less modern, no type hints
- Argparse: ❌ More boilerplate

---

### Decision 3: Template Engine
**Choice:** Use Jinja2 for file templates

**Rationale:**
- ✅ Industry-standard, well-tested
- ✅ Powerful template syntax
- ✅ Good documentation
- ✅ Widely known
- ❌ Additional dependency

**Alternatives:**
- String formatting: ❌ Too limited
- Custom DSL: ❌ Unnecessary complexity

---

### Decision 4: Rollback Strategy
**Choice:** Create full backup before modifications, restore on error

**Rationale:**
- ✅ Simple, reliable rollback
- ✅ Easy to test
- ✅ User can inspect backup if needed
- ❌ Requires disk space
- ❌ Slower for large projects

**Alternatives:**
- Transactional file system: ❌ Complex, OS-specific
- No rollback: ❌ Unsafe

---

### Decision 5: Distribution
**Choice:** Publish to PyPI as `fastmcp-create`

**Rationale:**
- ✅ Easy installation (`pip install fastmcp-create`)
- ✅ Works with pipx for global install
- ✅ Standard Python distribution
- ✅ Discoverable

**Alternatives:**
- Git submodule: ❌ Complex for users
- Shell script: ❌ Limited functionality

---

## Dependencies

### Runtime Dependencies
```toml
[project.dependencies]
typer = {extras = ["all"], version = "^0.9.0"}
rich = "^13.0.0"
jinja2 = "^3.1.0"
tomli = "^2.0.0"  # Python <3.11
tomli-w = "^1.0.0"
```

### Development Dependencies
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.8.0",
]
```

---

## Risks & Mitigation

### Risk 1: Breaking Template Updates
**Impact:** High - Script may break if template structure changes
**Probability:** Medium - Template will evolve over time
**Mitigation:**
- Pin script to specific template version
- Document compatible template versions
- Add validation checks for expected file structure
- Graceful degradation if optional files missing

### Risk 2: User Customizations Lost
**Impact:** High - Accidental data loss
**Probability:** Low - Only happens with `init` command
**Mitigation:**
- Require clean git state before `init`
- Create backup automatically
- Show diff before applying changes
- Add `--dry-run` flag

### Risk 3: Platform Compatibility
**Impact:** Medium - Script may not work on all platforms
**Probability:** Low - Python is cross-platform
**Mitigation:**
- Test on Linux, macOS, Windows
- Use pathlib for path handling
- Handle line endings correctly
- Document platform-specific issues

### Risk 4: Incomplete Cleanup
**Impact:** Medium - Demo tools remain in scaffolded project
**Probability:** Medium - Easy to miss cleanup locations
**Mitigation:**
- Comprehensive test suite
- Post-scaffold verification
- Checklist validation
- Clear error messages

---

## Timeline & Effort Estimation

**Total Estimated Effort:** 24-32 hours

**Breakdown by Task:**
- Task 01: Project Setup - 2-3 hours
- Task 02: File Operations - 2-3 hours
- Task 03: Demo Cleanup - 4-6 hours (most complex)
- Task 04: Templates - 3-4 hours
- Task 05: Metadata - 2 hours
- Task 06: Git Integration - 1-2 hours
- Task 07: Dependencies - 1-2 hours
- Task 08: Verification - 2-3 hours
- Task 09: Documentation - 2-3 hours
- Task 10: Testing & Publishing - 3-4 hours

**Phased Rollout:**
- **Phase 1 (MVP):** Tasks 01-05 (core functionality)
- **Phase 2:** Tasks 06-08 (optional features, verification)
- **Phase 3:** Tasks 09-10 (documentation, publishing)

---

## Future Enhancements

### Post-MVP Features
1. **Interactive Tool Generator** - Prompt for tool names, generate boilerplate
2. **Multiple Templates** - Support different MCP server types (REST API, WebSocket, etc.)
3. **Plugin System** - Allow custom cleanup/setup steps
4. **Configuration Presets** - Save/load configuration profiles
5. **Update Command** - Update existing projects to latest template
6. **Template Validation** - Check if template is compatible before scaffolding
7. **Rich Progress UI** - Animated progress with detailed steps
8. **Undo Command** - Reverse scaffolding if needed

---

## Success Metrics

**Quantitative:**
- Setup time reduced from 15-30 min → <2 min (90%+ reduction)
- Zero failing tests after scaffolding
- Zero linting errors after scaffolding
- 80%+ test coverage for script itself

**Qualitative:**
- Positive user feedback
- Adoption by fastmcp-template users
- Reduces onboarding friction for new MCP developers
- Becomes standard workflow for fastmcp-template projects

---

## References

- FastMCP Template Repo: https://github.com/l4b4r4b4b4/fastmcp-template
- Similar Tools:
  - `create-react-app` - React project scaffolding
  - `cookiecutter` - Python project templates
  - `copier` - Modern project generator
  - `yeoman` - Web app scaffolding

---

## Notes

- This script should be maintained in the fastmcp-template repo as `scripts/` or separate repo
- Consider making it a "blessed" tool recommended in fastmcp-template README
- Could be expanded to support other MCP frameworks beyond FastMCP
- Should follow the same `.rules` as the template itself
