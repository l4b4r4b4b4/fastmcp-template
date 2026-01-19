# Goals Index & Tracking Scratchpad

> Central hub for tracking all goals in {{ cookiecutter.project_name }}

---

## Active Goals

| ID | Goal Name | Status | Priority | Last Updated |
|----|-----------|--------|----------|--------------|
| 01 | Initial Setup & Release v0.0.0 | 🟡 In Progress | Critical | {{ cookiecutter.__year }}-01-01 |
| 02 | (Reserved) | ⚪ Not Started | - | - |
| 03 | (Reserved) | ⚪ Not Started | - | - |
| 04 | (Reserved) | ⚪ Not Started | - | - |
| 05 | (Reserved) | ⚪ Not Started | - | - |

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
- [01-Initial-Setup-And-Release](./01-Initial-Setup-And-Release/scratchpad.md) — Complete setup and validate release pipeline

---

## Goal Creation Guidelines

1. **Copy from template:** Use `00-Template-Goal/` as starting point
2. **Follow numbering:** Goals are `01-10-*`, tasks are `Task-01-*`
3. **Update this index:** Add new goals to the table above
4. **Reference, don't duplicate:** Link to detailed scratchpads instead of copying content

---

## Notes

- Each goal has its own directory under `.agent/goals/`
- Goals contain a `scratchpad.md` and one or more `Task-XX/` subdirectories
- Tasks are atomic, actionable units of work within a goal
- Follow `.rules` workflow: Research → Plan → Pitch → Implement → Document

---

## Recent Activity

- **{{ cookiecutter.__year }}-01-01:** Project generated with {{ cookiecutter.template_variant }} template variant
- **{{ cookiecutter.__year }}-01-01:** Goal 01 created - Initial Setup & Release v0.0.0
  - Critical first goal to validate entire development and release pipeline
  - Ensures project works out of the box and all workflows function
  - Publishing v0.0.0 validates packaging before real development begins