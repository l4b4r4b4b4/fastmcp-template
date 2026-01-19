# Goal 01: Initial Setup & Release v0.0.0

> Complete post-generation setup and validate the entire release pipeline

---

## Status: 🟡 In Progress

**Created:** {{ cookiecutter.__year }}-01-01
**Priority:** Critical
**Estimated Effort:** 1-2 hours

---

## Objective

Validate that {{ cookiecutter.project_name }} works correctly after generation by:
1. Setting up the development environment
2. Running all tests and quality checks
3. Publishing version 0.0.0 to test the complete release pipeline
4. Verifying all workflows function end-to-end

---

## Success Criteria

- [ ] Development environment setup complete (`uv sync` works)
- [ ] All tests pass (`pytest` with {% if cookiecutter.template_variant == "minimal" %}~60{% elif cookiecutter.template_variant == "standard" %}~75{% elif cookiecutter.template_variant == "full" %}~101{% else %}variable{% endif %} tests)
- [ ] Code quality checks pass (`ruff check` and `ruff format --check`)
- [ ] CI workflow passes on GitHub
- [ ] Version 0.0.0 successfully published to PyPI
- [ ] Docker image builds and publishes (if enabled)
- [ ] All workflows verified: CI → Release → Publish → CD

---

## Context & Background

This is the foundational goal for every generated project. The .rules file emphasizes:
> **First version is always 0.0.0** - Tests both initial implementation AND release workflow

Publishing 0.0.0 immediately serves two purposes:
1. **Validates the code works** - All tests pass, no import errors
2. **Validates the release pipeline** - Packaging, PyPI publishing, Docker builds all function

This goal follows the .rules philosophy of building confidence through incremental releases: `0.0.0 → 0.0.x → 0.1.0 → 1.0.0`

---

## Implementation Checklist

### Phase 1: Local Environment Setup
- [ ] Run `uv sync` to install dependencies
- [ ] Verify Python {{ cookiecutter.python_version }} is being used
- [ ] Check project structure matches expected layout

### Phase 2: Code Quality Verification
- [ ] Run `pytest` - expect {% if cookiecutter.template_variant == "minimal" %}~60{% elif cookiecutter.template_variant == "standard" %}~75{% elif cookiecutter.template_variant == "full" %}~101{% else %}variable{% endif %} passing tests
- [ ] Run `ruff check . --fix && ruff format .` - no issues
- [ ] Run `uv run python -c "import {{ cookiecutter.__project_slug_underscore }}; print('Import successful')"` - verify package imports

### Phase 3: Git and CI Setup
- [ ] Initialize git repository (if not already done)
- [ ] Set up GitHub repository: `{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}`
- [ ] Push initial commit to main branch
- [ ] Verify CI workflow passes (should run automatically on push)

### Phase 4: Release Pipeline Testing
- [ ] Create and push tag `v0.0.0`: `git tag v0.0.0 && git push origin v0.0.0`
- [ ] Verify Release workflow creates GitHub release
- [ ] Verify Publish workflow uploads to PyPI
{% if cookiecutter.template_variant != "minimal" %}- [ ] Verify Docker image builds and pushes to registry{% endif %}

### Phase 5: Verification
- [ ] Confirm package is available on PyPI: `https://pypi.org/project/{{ cookiecutter.project_slug }}/`
- [ ] Test installation in clean environment: `pip install {{ cookiecutter.project_slug }}==0.0.0`
- [ ] Verify MCP server starts: `{{ cookiecutter.project_slug }}`

---

## Configuration Summary

**Template Variant:** {{ cookiecutter.template_variant }}
**Components Included:**
{% if cookiecutter.include_demo_tools == "yes" %}- ✅ Demo tools (example MCP tools for learning){% else %}- ❌ Demo tools (minimal server only){% endif %}
{% if cookiecutter.include_secret_tools == "yes" %}- ✅ Secret tools (API key demonstrations){% else %}- ❌ Secret tools (no API examples){% endif %}
{% if cookiecutter.include_langfuse == "yes" %}- ✅ Langfuse integration (observability){% else %}- ❌ Langfuse integration (no observability){% endif %}

**Expected Test Count:** {% if cookiecutter.template_variant == "minimal" %}~60 tests{% elif cookiecutter.template_variant == "standard" %}~75 tests{% elif cookiecutter.template_variant == "full" %}~101 tests{% else %}Variable based on selected options{% endif %}

---

## Troubleshooting

### Common Issues

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| `uv sync` fails | Missing Python {{ cookiecutter.python_version }} | Install Python {{ cookiecutter.python_version }} with pyenv/conda |
| Tests fail | Template generation issue | Check for leftover `{%raw%}{{cookiecutter.*}}{%endraw%}` placeholders |
| CI fails | Missing GitHub secrets | Add required secrets to repository settings |
| PyPI publish fails | Package name taken | Choose different `project_slug` in cookiecutter |
| Docker build fails | Missing dependencies | Check Dockerfile has all required packages |

### Validation Commands

```bash
# Quick validation sequence
uv sync
pytest --tb=short
ruff check . --fix && ruff format .
uv run python -c "import {{ cookiecutter.__project_slug_underscore }}; print('✅ Import successful')"
```

---

## Dependencies

**Upstream:** None (this is the foundation goal)
**Downstream:** All future development depends on this working

---

## Notes & Decisions

### Why 0.0.0 First?
From .rules: "Starting at 0.0.0 accomplishes two critical goals:
1. **Tests implementation** - Validates the initial code works  
2. **Tests release workflow** - Forces you to get packaging right from day one"

The 0.0.0 release signals "experimental test release - expect issues" which is honest for a newly generated project.

### Template-Specific Expectations
{% if cookiecutter.template_variant == "minimal" %}**Minimal Variant:** Bare-bones server with ~60 tests. Perfect for learning MCP basics or building custom tools from scratch.{% endif %}
{% if cookiecutter.template_variant == "standard" %}**Standard Variant:** Balanced feature set with ~75 tests. Good default for most MCP server projects.{% endif %}
{% if cookiecutter.template_variant == "full" %}**Full Variant:** All features enabled with ~101 tests. Complete example for production-ready servers.{% endif %}
{% if cookiecutter.template_variant == "custom" %}**Custom Variant:** User-selected features. Test count varies based on included components.{% endif %}

---

## References

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP RefCache Documentation](https://github.com/l4b4r4b4b4/mcp-refcache)
- [Project .rules file](../../.rules) - Development guidelines
- [PyPI Project Page](https://pypi.org/project/{{ cookiecutter.project_slug }}/) - After 0.0.0 release