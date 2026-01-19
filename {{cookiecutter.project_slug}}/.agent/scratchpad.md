# Main Session Scratchpad

> Current session state and quick navigation for {{ cookiecutter.project_name }}

---

## Current Status

**Last Updated:** {{ cookiecutter.__year }}-01-01
**Active Goal:** [Goal 01: Initial Setup & Release v0.0.0](.agent/goals/01-Initial-Setup-And-Release/scratchpad.md)

---

## Quick Navigation

### Goals
- [Goals Index](.agent/goals/scratchpad.md) - All project goals
- [Goal 01: Initial Setup & Release](.agent/goals/01-Initial-Setup-And-Release/scratchpad.md) - 🟡 In Progress

---

## Recent Session Notes

- **Project Generated:** {{ cookiecutter.__year }}-01-01
- **Next Action:** Complete Goal 01 - validate entire release pipeline with v0.0.0
- **Environment:** {{ cookiecutter.template_variant }} variant
{% if cookiecutter.include_demo_tools == "yes" %}  - Demo tools included{% endif %}
{% if cookiecutter.include_secret_tools == "yes" %}  - Secret tools included{% endif %}
{% if cookiecutter.include_langfuse == "yes" %}  - Langfuse integration enabled{% endif %}

---

## Development Workflow

### First Steps (Goal 01)
1. Run `uv sync` to install dependencies
2. Run `pytest` to verify all tests pass
3. Run `ruff check . && ruff format --check .` for linting
4. Push to GitHub and verify CI passes
5. Create v0.0.0 tag to test release pipeline

### Daily Workflow
- Follow `.rules` workflow: Research → Plan → Pitch → Implement → Document
- Update this scratchpad with session state
- Keep detailed work in individual goal/task scratchpads

---

## Development Environment

**Python:** {{ cookiecutter.python_version }}
**Package Manager:** uv
**Main Dependencies:**
- FastMCP: {{ cookiecutter.fastmcp_version }}
- MCP RefCache: {{ cookiecutter.mcp_refcache_version }}
{% if cookiecutter.include_langfuse == "yes" %}- Langfuse: {{ cookiecutter.langfuse_version }}{% endif %}
- Pydantic: {{ cookiecutter.pydantic_version }}

**Project Structure:**
```
{{ cookiecutter.project_slug }}/
├── src/{{ cookiecutter.__project_slug_underscore }}/
├── tests/
├── .agent/                  # AI assistant workspace
└── pyproject.toml
```

---

## Notes

- This scratchpad tracks HIGH-LEVEL session state only
- Detailed planning goes in individual goal/task scratchpads
- Link to detailed scratchpads, don't duplicate content
- Update frequently to maintain context across sessions