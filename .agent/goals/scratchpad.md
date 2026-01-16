# Goals Index & Tracking Scratchpad

> Central hub for tracking all active goals in the nix-configs repository.

---

## Active Goals

| ID | Goal Name | Status | Priority | Last Updated |
|----|-----------|--------|----------|--------------|
| 01 | Fix Cookiecutter Templating | 🟢 Complete | High | 2025-01-08 |
| 02 | Fix Demo Tools & Tests Consistency | 🟢 Complete | High | 2025-01-08 |
| 03 | Add Minimal Tools Option | 🟢 Complete | Medium | 2025-01-08 |
| 04 | Enforce CI-Gated Workflow | 🟢 Complete | High | 2025-01-08 |
| 05 | Add Template CI Testing | ⚪ Not Started | High | 2025-01-08 |
| 06 | Add Template Variants | ⚪ Not Started | Medium | 2025-01-08 |
| 07 | Add Example Integrations | ⚪ Not Started | Medium | 2025-01-08 |
| 08 | (Reserved) | ⚪ Not Started | - | - |
| 09 | (Reserved) | ⚪ Not Started | - | - |
| 10 | (Reserved) | ⚪ Not Started | - | - |

---

## Archived Goals

| ID | Goal Name | Status | Archived Date | Reason |
|----|-----------|--------|---------------|---------|
| A01 | Add API Key Checker | ⚫ Archived | 2025-01-08 | Superseded by other priorities |
| A02 | FastMCP Template Scaffolding Script | 🟢 Complete | 2025-01-08 | All 4 tasks completed successfully |

---

## Status Legend

- 🟢 **Complete** — Goal achieved and verified
- 🟡 **In Progress** — Actively being worked on
- 🔴 **Blocked** — Waiting on external dependency or decision
- ⚪ **Not Started** — Planned but not yet begun
- ⚫ **Archived** — Abandoned or superseded

---

## Priority Levels

- **Critical** — Blocking other work or system stability
- **High** — Important for near-term objectives
- **Medium** — Should be addressed when time permits
- **Low** — Nice to have, no urgency

---

## Quick Links

- [00-Template-Goal](./00-Template-Goal/scratchpad.md) — Template for new goals
- [01-Fix-Cookiecutter-Templating](./01-Fix-Cookiecutter-Templating/scratchpad.md) — Fix hardcoded values in 21 files
- [02-Fix-Demo-Tools-Test-Consistency](./02-Fix-Demo-Tools-Test-Consistency/scratchpad.md) — Make tests conditional on include_demo_tools
- [03-Add-Minimal-Tools-Option](./03-Add-Minimal-Tools-Option/scratchpad.md) — Add include_secret_tools option
- [04-Enforce-CI-Gated-Workflow](./04-Enforce-CI-Gated-Workflow/scratchpad.md) — Ensure release/publish/deploy require CI pass
- [05-Add-Template-CI-Testing](./05-Add-Template-CI-Testing/scratchpad.md) — Test template generation in CI
- [06-Add-Template-Variants](./06-Add-Template-Variants/scratchpad.md) — Add preset configurations (minimal, standard, full)
- [07-Add-Example-Integrations](./07-Add-Example-Integrations/scratchpad.md) — Add real-world integration examples

### Archived Goals
- [A01-Add-API-Key-Checker](./archived/01-Add-API-Key-Checker/scratchpad.md) — Archived (superseded)
- [A02-FastMCP-Template-Scaffolding-Script](./archived/02-FastMCP-Template-Scaffolding-Script/scratchpad.md) — Complete (cookiecutter conversion)

---

## Notes

- Each goal has its own directory under `.agent/goals/`
- Goals contain a `scratchpad.md` and one or more `Task-XX/` subdirectories
- Tasks are atomic, actionable units of work within a goal
- Use the template in `00-Template-Goal/` when creating new goals

---

## Recent Activity

- **2025-01-08:** Goals 05-07 Created - Future Enhancements 📋
  - Goal 05: Add Template CI Testing - Automated testing of all configurations
  - Goal 06: Add Template Variants - Preset configurations (@minimal, @standard, @full)
  - Goal 07: Add Example Integrations - Real-world patterns (database, API, filesystem, services)
  - Total estimated effort: 9-13 hours
  - All goals documented and ready for implementation

- **2025-01-08:** Goal 04 Complete - Enforce CI-Gated Workflow ✅
  - Added CI verification for tag pushes in release.yml (25 lines)
  - Added Release workflow verification to publish.yml (39 lines)
  - Updated pre-commit with --unsafe-fixes flag
  - Documented branch protection setup in CONTRIBUTING.md (88 lines)
  - Added CI/CD workflow diagram to README.md (46 lines)
  - Total: ~198 lines across 5 files
  - All workflows now have explicit verification gates
  - Comprehensive documentation for repository setup

- **2025-01-08:** Goal 03 Complete - Add Minimal Tools Option ✅
  - Added `include_secret_tools` cookiecutter option (default "no")
  - Made secret tool imports conditional in app/tools/__init__.py
  - Made secret tool registration conditional in app/server.py (3 locations)
  - Wrapped 2 secret test classes + 6 individual tests with conditionals
  - Updated README.md with configuration options table
  - Verified all 4 combinations work:
    • Minimal (no/no): 74 tests pass (3.37s)
    • Full (yes/yes): 101 tests pass (3.04s)
    • Demos only (yes/no): 86 tests pass (3.36s)
    • Secrets only (no/yes): 85 tests pass (4.19s)
  - Template now supports truly minimal servers with no demo code

- **2025-01-08:** Goal 02 Complete - Fix Demo Tools & Tests Consistency ✅
  - Wrapped 4 test classes with Jinja conditionals in tests/test_server.py
  - Made demo tool imports conditional in app/tools/__init__.py
  - Verified: include_demo_tools="no" → 85 tests pass (4.52s)
  - Verified: include_demo_tools="yes" → 101 tests pass (4.44s)
  - Added minimal pyproject.toml to template repo for cookiecutter dev dependency
  - Template now correctly includes/excludes demo tools and tests based on option

- **2025-01-08:** Goal 01 Complete - Fix Cookiecutter Templating ✅
  - Fixed 79 hardcoded references across 22 files
  - Original scope: 20 files, 70 references
  - Found during verification: 2 Docker files, 9 additional references
  - Completed all 6 tasks: GitHub Workflows, App Source, Tests, Docs, Config, Verification
  - Generated test project: 0 hardcoded references remaining
  - All 101 tests pass with demo tools enabled
  - Template now fully functional for generating customized projects

- **2025-01-08:** Goals Reorganization
  - Archived Goal A01 (API Key Checker) - superseded by other priorities
  - Archived Goal A02 (FastMCP Template Scaffolding) - completed successfully (all 4 tasks ✅)
  - Promoted Goal 03 → Goal 01 (Fix Cookiecutter Templating)
  - Renumbered remaining goals: 04→02, 05→03, 06→04

- **2025-01-08:** Goal A02 Completed - FastMCP Template Scaffolding Script
  - ✅ Task 01: Created cookiecutter.json with 17 variables
  - ✅ Task 02: Restructured repository for cookiecutter pattern
  - ✅ Task 03: Converted 15+ files to Jinja2 templates
  - ✅ Task 04: Created post-generation hooks with automation
  - Template is now fully functional with `cookiecutter . --no-input`

- **2025-01-08:** Goal 01 (Now Active) - Fix Cookiecutter Templating
  - Found 74 hardcoded references across 21 files
  - Includes `fastmcp-template`, `FastMCP Template`, `l4b4r4b4b4`
  - Need to template with `{{ cookiecutter.project_slug }}` and `{{ cookiecutter.github_username }}`
  - High priority: Users get hardcoded values instead of their project settings

- **2025-01-08:** Created Goal 04 - Enforce CI-Gated Workflow
  - Release workflow tag pushes currently bypass CI verification
  - Publish workflow has no CI gate at all
  - Need to chain: CI → Release → Publish → CD

- **2025-01-08:** Created Goal 03 - Add Minimal Tools Option
  - Add `include_secret_tools` option to remove secret demo tools
  - Allows generating truly minimal servers without demo/example code
  - Depends on Goals 01 and 02

- **2025-01-08:** Created Goal 02 - Fix Demo Tools & Tests Consistency
  - Tests for demo tools fail when `include_demo_tools="no"`
  - Need to wrap demo tests with `{% if cookiecutter.include_demo_tools == "yes" %}`
  - Also affects `app/tools/__init__.py` imports
