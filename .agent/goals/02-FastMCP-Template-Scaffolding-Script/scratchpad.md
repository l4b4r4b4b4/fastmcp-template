# Goal 02: FastMCP Template Scaffolding Script

**Status:** ⚪ Not Started
**Priority:** Medium
**Created:** 2025-01-08
**Last Updated:** 2025-01-08

---

## Overview

Create a CLI scaffolding script (similar to `create-react-app`) that automates the cleanup and customization of the fastmcp-template repository when starting a new project. This eliminates repetitive manual steps like removing demo tools, updating server names, cleaning up documentation, and configuring project-specific settings.

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
1. **Automation** - Single command to scaffold a clean project
2. **Consistency** - Every new project starts from the same clean baseline
3. **Speed** - Reduce setup time from 15-30 minutes to <2 minutes
4. **Safety** - Preserve project structure, don't break existing files
5. **Flexibility** - Support different project types (HTTP API, stdio, etc.)

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
# Install globally (once)
pip install fastmcp-create
# or
pipx install fastmcp-create

# Create new project
fastmcp-create my-mcp-server

# Interactive prompts:
# - Project name: my-mcp-server
# - Description: My awesome MCP server
# - Author: Your Name <you@example.com>
# - Server type: [stdio | http | both] (default: stdio)
# - Initialize git? [y/N]
# - Install dependencies? [Y/n]

# Output:
# ✓ Created project directory: ./my-mcp-server
# ✓ Cleaned up demo tools
# ✓ Updated server configuration
# ✓ Updated project metadata
# ✓ Removed demo tests
# ✓ Cleaned documentation
# ✓ Initialized git repository
# ✓ Installed dependencies
#
# Next steps:
#   cd my-mcp-server
#   uv run pytest
#   uv run my-mcp-server stdio
#
# Your FastMCP server is ready! 🚀
```

### Alternative: In-Place Cleanup

```bash
# For when you've already cloned the template
cd my-existing-project
fastmcp-init

# Interactive prompts same as above
# Cleans up current directory instead of creating new one
```

---

## Technical Design

### Script Structure

```
fastmcp-create/
├── pyproject.toml           # Package metadata
├── README.md                # Usage documentation
├── src/
│   └── fastmcp_create/
│       ├── __init__.py
│       ├── __main__.py      # CLI entry point
│       ├── cli.py           # CLI interface (typer)
│       ├── scaffold.py      # Main scaffolding logic
│       ├── templates.py     # Template file generators
│       ├── cleanup.py       # Demo tool removal
│       ├── config.py        # Configuration management
│       └── utils.py         # File operations, validation
└── tests/
    ├── test_scaffold.py
    ├── test_cleanup.py
    └── fixtures/            # Test templates
```

### Core Components

#### 1. CLI Interface (`cli.py`)
- Uses `typer` for interactive CLI
- Two commands: `create` (new dir) and `init` (in-place)
- Interactive prompts with validation
- Progress indicators during long operations

#### 2. Scaffolding Engine (`scaffold.py`)
- Orchestrates all cleanup/setup steps
- Atomic operations (rollback on failure)
- Progress reporting
- Post-scaffold verification

#### 3. Demo Tool Cleanup (`cleanup.py`)
- Removes demo tools from `app/server.py`
- Removes demo tool implementations
- Removes demo tests from `tests/test_server.py`
- Updates `app/prompts/__init__.py`
- Updates `app/tools/__init__.py` exports

#### 4. Template Generator (`templates.py`)
- Generates starter `server.py` with minimal tools
- Generates README with project-specific content
- Generates updated prompts
- Generates starter tool structure (optional)

#### 5. Configuration (`config.py`)
- Project metadata (name, description, author)
- Server type (stdio, http, both)
- Optional features (tracing, cache namespaces)
- Validation and defaults

---

## Implementation Tasks

### Task 01: Project Setup & CLI Framework
**Goal:** Create package structure and basic CLI interface

**Subtasks:**
- [ ] Create `fastmcp-create` package structure
- [ ] Set up `pyproject.toml` with dependencies (typer, rich, jinja2)
- [ ] Create CLI entry points (`fastmcp-create`, `fastmcp-init`)
- [ ] Implement basic `typer` command structure
- [ ] Add `--help` documentation
- [ ] Write initial tests for CLI parsing

**Dependencies:**
- `typer[all]` - CLI framework with rich output
- `rich` - Beautiful terminal output
- `jinja2` - Template rendering
- `pyyaml` - Configuration files (optional)
- `questionary` - Enhanced interactive prompts (alternative to typer)

**Estimated Effort:** 2-3 hours

---

### Task 02: File Operation Utilities
**Goal:** Safe file manipulation with rollback support

**Subtasks:**
- [ ] Implement atomic file operations (copy, move, delete)
- [ ] Create backup/restore mechanism
- [ ] Add path validation and safety checks
- [ ] Implement rollback on error
- [ ] Write tests for file operations

**Key Functions:**
```python
def safe_copy(src: Path, dst: Path) -> None
def safe_move(src: Path, dst: Path) -> None
def safe_delete(path: Path) -> None
def backup_project(project_path: Path) -> Path
def restore_backup(backup_path: Path, project_path: Path) -> None
```

**Estimated Effort:** 2-3 hours

---

### Task 03: Demo Tool Cleanup Logic
**Goal:** Remove all demo tool references from template

**Subtasks:**
- [ ] Parse and clean `app/server.py`:
  - Remove demo tool imports
  - Remove tool registration (@mcp.tool decorators)
  - Remove cached tool functions
  - Update server instructions
- [ ] Clean `app/prompts/__init__.py`:
  - Remove demo tool examples
  - Replace with generic starter text
- [ ] Clean `tests/test_server.py`:
  - Remove TestHelloTool, TestGenerateItems, etc.
  - Update assertions for new server name
- [ ] Clean `app/tools/` directory:
  - Remove `demo.py`, `secrets.py` (if present)
  - Update `__init__.py` exports
- [ ] Write comprehensive tests

**Key Functions:**
```python
def remove_demo_tools_from_server(server_py: Path) -> None
def clean_prompt_templates(prompts_init: Path) -> None
def remove_demo_tests(test_server_py: Path) -> None
def clean_tool_exports(tools_init: Path) -> None
```

**AST Manipulation:**
- Use `ast` module to parse Python files
- Remove specific function/class definitions
- Remove import statements
- Regenerate clean Python code

**Estimated Effort:** 4-6 hours

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
