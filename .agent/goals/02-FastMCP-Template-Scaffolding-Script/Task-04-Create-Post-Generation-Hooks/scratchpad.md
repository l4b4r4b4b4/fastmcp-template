# Task 04: Create Post-Generation Hooks

**Status:** 🟢 Complete
**Priority:** High
**Created:** 2025-01-08
**Completed:** 2025-01-08
**Estimated Effort:** 1 hour
**Actual Effort:** 1 hour

---

## Objective

Create Cookiecutter post-generation hooks to automate setup tasks after project generation:
- Install dependencies with `uv sync`
- Initialize Git repository
- Create initial commit
- Print success message with next steps

---

## Research & Context

### Cookiecutter Hooks Overview

Cookiecutter supports two types of hooks:
1. **Pre-generation hooks** (`hooks/pre_gen_project.py`) - Run before template generation
2. **Post-generation hooks** (`hooks/post_gen_project.py`) - Run after template generation

**Key Facts:**
- Hooks are Python scripts executed in the generated project directory
- Have access to `cookiecutter` dict via environment variables (JSON format)
- Exit code 0 = success, non-zero = failure (deletes generated project)
- Can run shell commands, create files, modify content
- Should handle errors gracefully and provide helpful messages

### Common Post-Generation Tasks

**Standard setup tasks:**
1. **Dependency installation** - `uv sync` to install all dependencies
2. **Git initialization** - `git init` + initial commit
3. **Build verification** - Run linters, formatters, tests
4. **File cleanup** - Remove files based on user choices
5. **Success message** - Print next steps for user

**Best Practices:**
- Check if commands exist before running (e.g., `git`, `uv`)
- Provide clear error messages if something fails
- Don't fail the whole generation for non-critical errors
- Print helpful next steps at the end
- Keep output concise and user-friendly

### Accessing Template Variables

```python
import os
import json

# Cookiecutter passes context as JSON in environment
cookiecutter_dict = json.loads(os.environ.get('COOKIECUTTER_CONTEXT_FILE', '{}'))

# Or use simpler approach with individual env vars
project_slug = "{{ cookiecutter.project_slug }}"  # Rendered in hook file
```

---

## Implementation Plan

### Step 1: Create hooks/ Directory
```bash
mkdir -p hooks/
```

### Step 2: Create post_gen_project.py

**Structure:**
```python
#!/usr/bin/env python3
"""Post-generation hook for FastMCP template."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"→ {description}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  ✓ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {description} failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"  ✗ Command not found: {cmd[0]}")
        return False

def main():
    """Run post-generation setup tasks."""
    print("\n" + "="*60)
    print("Setting up your FastMCP project...")
    print("="*60 + "\n")
    
    # Task 1: Install dependencies
    if not run_command(["uv", "sync"], "Installing dependencies"):
        print("\n⚠ Warning: Dependency installation failed")
        print("  Run 'uv sync' manually to install dependencies\n")
    
    # Task 2: Initialize git repository
    if not run_command(["git", "init"], "Initializing Git repository"):
        print("\n⚠ Warning: Git initialization failed")
        print("  Run 'git init' manually if you want version control\n")
    else:
        # Task 3: Create initial commit
        run_command(["git", "add", "."], "Staging files")
        run_command(
            ["git", "commit", "-m", "Initial commit from FastMCP template"],
            "Creating initial commit"
        )
    
    # Success message
    project_slug = "{{ cookiecutter.project_slug }}"
    print("\n" + "="*60)
    print(f"✓ Project '{project_slug}' created successfully!")
    print("="*60 + "\n")
    
    print("Next steps:")
    print(f"  1. cd {project_slug}")
    print("  2. uv run pytest              # Run tests")
    print("  3. uv run fastmcp dev app/server.py  # Start development server")
    print("\nFor more information, see README.md\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Post-generation hook failed: {e}", file=sys.stderr)
        sys.exit(1)
```

### Step 3: Make Hook Executable
```bash
chmod +x hooks/post_gen_project.py
```

### Step 4: Test Hook

**Test 1: Generate with defaults**
```bash
cd /tmp
cookiecutter ~/code/github.com/l4b4r4b4b4/mcp-refcache/examples/fastmcp-template --no-input
# Should see:
# → Installing dependencies...
# → Initializing Git repository...
# → Creating initial commit...
# ✓ Project 'fastmcp-template' created successfully!
```

**Test 2: Verify generated project**
```bash
cd fastmcp-template
uv run pytest  # Should work (deps installed)
git log  # Should have initial commit
```

**Test 3: Test with custom name**
```bash
cookiecutter ~/path/to/template --no-input project_name="Weather API"
cd weather-api
uv run pytest
```

---

## Files Created/Modified

- [x] `hooks/post_gen_project.py` - Main post-generation script ✅
- [x] `flake.nix` - Root-level Nix development environment (NEW) ✅
- [x] `.zed/settings.json` - Root-level Zed editor config (NEW) ✅

---

## Acceptance Criteria

- [x] Hook runs after project generation ✅
- [x] Dependencies installed automatically with `uv sync` ✅
- [x] Git repository initialized ✅
- [x] Initial commit created ✅
- [x] Success message printed with next steps ✅
- [x] Errors handled gracefully (don't fail generation) ✅
- [x] Commands check for tool availability ✅
- [x] Output is user-friendly and concise ✅
- [x] Hook works in both interactive and non-interactive modes ✅
- [x] Generated project is immediately usable ✅

---

## Edge Cases to Handle

### 1. Missing Tools
- User doesn't have `uv` installed → Print warning, continue
- User doesn't have `git` installed → Print warning, continue
- Don't fail generation, just skip optional steps

### 2. Command Failures
- `uv sync` fails (network issue, broken deps) → Warn user
- `git init` fails (already a repo, permissions) → Warn user
- Capture stderr and show helpful message

### 3. Existing Git Repository
- User generates template inside existing repo
- `git init` will fail → Handle gracefully

### 4. Network Issues
- `uv sync` requires network to download packages
- May fail in offline environments → Provide manual instructions

---

## Alternative Approaches Considered

### Option 1: Minimal Hook (No Automation)
Just print instructions, don't run commands.

**Pros:** Can't fail, works everywhere
**Cons:** User has to run commands manually (defeats purpose)

**Verdict:** ❌ Not chosen - automation is the goal

### Option 2: Full Automation (Exit on Failure)
Run all commands, exit non-zero if any fail.

**Pros:** Ensures project is fully set up
**Cons:** Fails generation if `uv` or `git` missing

**Verdict:** ❌ Not chosen - too strict

### Option 3: Graceful Degradation (Warn on Failure) ✅
Run commands, warn if they fail, but continue.

**Pros:** Best user experience, still generates project
**Cons:** User might not notice warnings

**Verdict:** ✅ **Chosen** - Best balance of automation and flexibility

---

## Testing Strategy

1. **Test with all tools available:**
   ```bash
   cookiecutter . --no-input
   # Verify: deps installed, git repo initialized, commit created
   ```

2. **Test without git:**
   ```bash
   PATH=/usr/bin:$PATH cookiecutter . --no-input  # Remove git from PATH
   # Verify: deps installed, warning printed, project still created
   ```

3. **Test without uv:**
   ```bash
   PATH=/usr/bin:$PATH cookiecutter . --no-input  # Remove uv from PATH
   # Verify: warning printed, project still created
   ```

4. **Test in existing git repo:**
   ```bash
   cd /tmp && git init test-repo && cd test-repo
   cookiecutter ~/path/to/template --no-input
   # Verify: handles git init failure gracefully
   ```

5. **Test generated project works:**
   ```bash
   cd generated-project
   uv run pytest  # Should pass
   uv run ruff check .  # Should pass
   uv run fastmcp dev app/server.py  # Should start server
   ```

---

## Notes

- Keep hook simple and focused
- Don't add too many automated steps (tests, builds, etc.)
- Let user decide when to run those
- Hook should complete in < 10 seconds for good UX

---

## Completion Log

### 2025-01-08 - Task Complete ✅

**Files Created:**

1. **`hooks/post_gen_project.py`** (163 lines) - Post-generation automation script
   - Installs dependencies with `uv sync`
   - Initializes git repository with `git init`
   - Creates initial commit
   - Prints success message with next steps
   - Handles missing tools gracefully (warns, doesn't fail)
   - Checks if already in git repo (skips init if so)
   - User-friendly output with emoji indicators

2. **`flake.nix`** (102 lines) - Root-level Nix development environment
   - Python 3.12 and uv
   - **cookiecutter** - For template development/testing
   - Development tools (git, curl, jq, tree)
   - FHS environment with zsh shell
   - Template-specific quick reference guide
   - Excludes project-specific MCP servers (this is for template development)

3. **`.zed/settings.json`** (76 lines) - Root-level Zed editor configuration
   - Python formatting with ruff
   - LSP configuration for pyright
   - Proper exclusions (no MCP server configs)
   - Tab sizes for various languages
   - Git gutter and terminal settings

**Hook Features:**

```python
# Key features of post_gen_project.py:
- run_command() helper with graceful error handling
- check_command_exists() to verify tools available
- Detects if already in git repo (skips git init)
- Non-critical failures don't abort generation
- Clear warnings for missing tools (uv, git)
- Helpful next steps printed at end
- Proper error handling (KeyboardInterrupt, exceptions)
```

**Testing Results:**

✅ **Test 1: Default generation (no demo tools)**
```bash
uvx cookiecutter . --no-input --output-dir /tmp/test-complete
# Result: ✅ Generated successfully
#         ✅ Dependencies installed
#         ✅ Git initialized with initial commit
#         ✅ 96 tests pass (5 demo tool tests skipped as expected)
```

✅ **Test 2: With demo tools enabled**
```bash
uvx cookiecutter . --no-input include_demo_tools="yes" --output-dir /tmp/test-with-demos
# Result: ✅ All 101 tests pass
#         ✅ Demo tools included and working
#         ✅ Project immediately usable
```

✅ **Test 3: Hook output verification**
```
======================================================================
Setting up 'FastMCP Template'...
======================================================================

→ Installing dependencies...
  ✓ Installing dependencies complete
→ Initializing Git repository...
  ✓ Initializing Git repository complete
→ Staging files...
  ✓ Staging files complete
→ Creating initial commit...
  ✓ Creating initial commit complete

======================================================================
✓ Project 'FastMCP Template' created successfully!
======================================================================

Next steps:
  1. cd fastmcp-template
  2. uv run pytest              # Run tests
  3. uv run ruff check .        # Check code quality
  4. uv run fastmcp dev app/server.py  # Start development server
```

**Root Development Environment:**

The template repository now has its own development environment:

1. **`flake.nix`** - Nix development shell
   - Includes `cookiecutter` for testing template generation
   - Includes `uv` for Python tooling
   - Template-specific quick reference commands
   - No MCP servers (those are for generated projects)

2. **`.zed/settings.json`** - Editor configuration
   - Python/Nix/YAML/TOML formatting
   - No MCP server configs (template development only)
   - Proper file exclusions

**Key Design Decisions:**

1. **Graceful degradation** - Hook warns but doesn't fail if tools missing
   - Missing `uv`: Prints installation instructions, continues
   - Missing `git`: Warns user, continues
   - Network issues: Warns about `uv sync` failure, continues

2. **Smart git handling** - Detects existing git repositories
   - Checks `git rev-parse --git-dir` before `git init`
   - Prints info message if already in repo
   - Avoids errors from duplicate initialization

3. **Clear output** - User-friendly messages
   - → for in-progress tasks
   - ✓ for successful tasks
   - ✗ for failed tasks
   - ⚠️ for warnings
   - Contextual next steps based on tool availability

4. **Separate template dev environment** - Root-level files
   - Template repo has own flake.nix with cookiecutter
   - Template repo has own .zed/settings.json without MCP servers
   - Generated projects have their own environment (in template)

**Edge Cases Handled:**

- ✅ Missing `uv` command
- ✅ Missing `git` command
- ✅ Already in git repository
- ✅ Network failures during `uv sync`
- ✅ Permission errors
- ✅ Keyboard interrupt (Ctrl+C)
- ✅ Unexpected exceptions

**Git & PR:**

- ✅ Branch pushed: `feature/goal-02-scaffolding-script`
- ✅ Pull Request created: #9 - "Convert FastMCP Template to Cookiecutter Format"
  - URL: https://github.com/l4b4r4b4b4/fastmcp-template/pull/9
  - Base: main
  - Comprehensive PR description with all tasks, testing results, usage examples
- ⏳ Awaiting review and merge

**Next Steps:**

Task 04 is complete. PR created and ready for review/merge.

Once merged to main, users can generate projects with:
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template
```

Task 05 will focus on final testing and documentation updates after merge.