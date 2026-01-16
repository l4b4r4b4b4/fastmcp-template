# Goal 05: Add Template CI Testing

## Status: 🟡 In Progress

**Created:** 2025-01-08
**Updated:** 2025-01-16
**Priority:** High
**Estimated Effort:** 2-3 hours
**Depends On:** 
- ✅ Goal 01 (Fix Cookiecutter Templating) - Complete
- ✅ Goal 02 (Fix Demo Tools Test Consistency) - Complete
- ✅ Goal 03 (Add Minimal Tools Option) - Complete
- ✅ Goal 04 (Enforce CI-Gated Workflow) - Complete

---

## Objective

Add CI workflow to the template repository itself that tests cookiecutter template generation. This catches template issues before users encounter them and validates that all configuration combinations work correctly.

---

## Problem Description

Currently, the template repository has no automated testing:
- ❌ No verification that template generates successfully
- ❌ No validation that all 4 configurations work
- ❌ No test that generated projects pass their tests
- ❌ Changes to template could break generation without warning
- ❌ Manual testing required for every change

This means:
1. Template bugs might reach users
2. Breaking changes aren't caught early
3. Contributors can't verify their changes
4. Maintenance is riskier and slower

---

## Proposed Solution

Add `.github/workflows/test-template.yml` that:
1. Tests cookiecutter generation for all 4 configurations
2. Runs pytest in each generated project
3. Verifies linting passes
4. Checks for common issues (hardcoded values, broken imports)

---

## Implementation Plan

### Task 01: Create Template Test Workflow

**File:** `.github/workflows/test-template.yml`

**Triggers:**
- Pull requests
- Push to main
- Manual dispatch

**Jobs:**

1. **test-generation** - Matrix test all 4 configurations
   ```yaml
   strategy:
     matrix:
       config:
         - name: minimal
           demo_tools: no
           secret_tools: no
           expected_tests: 74
         - name: full
           demo_tools: yes
           secret_tools: yes
           expected_tests: 101
         - name: demos-only
           demo_tools: yes
           secret_tools: no
           expected_tests: 86
         - name: secrets-only
           demo_tools: no
           secret_tools: yes
           expected_tests: 85
   ```

2. **Steps per configuration:**
   - Checkout template repo
   - Install cookiecutter (use uv from pyproject.toml)
   - Generate project with specific config
   - Run pytest and verify test count
   - Run ruff check
   - Check for hardcoded values (grep for "fastmcp-template")

### Task 02: Add Template Validation Script

**File:** `scripts/validate-template.sh`

**Purpose:** Helper script for local testing and CI

**Functions:**
- Generate with specific config
- Run all checks (tests, lint, validation)
- Report results
- Clean up temp directories

**Usage:**
```bash
./scripts/validate-template.sh minimal
./scripts/validate-template.sh full
./scripts/validate-template.sh --all
```

### Task 03: Add Pre-commit Hook for Template Files

**File:** `.pre-commit-config.yaml` (template repo root)

**Add hook:**
```yaml
- repo: local
  hooks:
    - id: check-jinja-syntax
      name: Check Jinja2 syntax
      entry: python -c "from jinja2 import Environment; import sys; [Environment().parse(open(f).read()) for f in sys.argv[1:]]"
      language: system
      files: '\{\{cookiecutter.*\}\}'
```

### Task 04: Add README Section on Testing

**File:** `README.md` (template repo)

**Add section:**
```markdown
## Testing the Template

### Automated Testing

CI automatically tests all 4 configurations on every PR and push to main.

### Manual Testing

Test a specific configuration:
```bash
./scripts/validate-template.sh minimal
```

Test all configurations:
```bash
./scripts/validate-template.sh --all
```

### Before Submitting PR

1. Test your changes locally:
   ```bash
   uv run cookiecutter . --output-dir /tmp
   cd /tmp/your-test-project
   uv run pytest
   ```

2. Verify all configurations work:
   ```bash
   ./scripts/validate-template.sh --all
   ```
```

### Task 05: Update Contributing Guidelines

**File:** `CONTRIBUTING.md` (template repo)

**Add section on template development:**
- How to test changes locally
- What CI checks for
- How to add new configuration options
- Testing checklist for PRs

---

## Acceptance Criteria

- [ ] CI workflow tests all 4 configurations
- [ ] Each configuration verified to generate successfully
- [ ] Each generated project runs pytest with expected test count
- [ ] Ruff linting checked for generated projects
- [ ] Validation script works locally
- [ ] Pre-commit hook checks Jinja syntax (optional)
- [ ] Documentation explains testing process
- [ ] CI badge added to template repo README

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `.github/workflows/test-template.yml` | Create | CI workflow for testing |
| `scripts/validate-template.sh` | Create | Local testing helper |
| `.pre-commit-config.yaml` (template repo) | Create/Update | Jinja syntax validation |
| `README.md` (template repo) | Update | Testing documentation |
| `CONTRIBUTING.md` (template repo) | Update | Development guidelines |

---

## Test Matrix

| Configuration | demo_tools | secret_tools | Expected Tests | CI Check |
|---------------|------------|--------------|----------------|----------|
| Minimal | no | no | 74 | ✅ Must pass |
| Full | yes | yes | 101 | ✅ Must pass |
| Demos Only | yes | no | 86 | ✅ Must pass |
| Secrets Only | no | yes | 85 | ✅ Must pass |

---

## Benefits

**For Maintainers:**
- ✅ Catch breaking changes automatically
- ✅ Confidence when merging PRs
- ✅ Regression prevention
- ✅ Faster review cycle

**For Contributors:**
- ✅ Clear testing expectations
- ✅ Validation before submitting
- ✅ Fast feedback on changes
- ✅ No surprises in review

**For Users:**
- ✅ Higher template quality
- ✅ Fewer bugs in generated projects
- ✅ Trust in template stability

---

## Implementation Notes

- Use uv from template's pyproject.toml (already has cookiecutter)
- Matrix strategy keeps configurations DRY
- Test count verification catches missing/extra tests
- Hardcoded value check prevents Goal 01 regression
- Each config runs in ~5-10 seconds (parallel execution)

---

## Future Enhancements

After initial implementation:
- Add workflow timing benchmarks
- Test Docker builds in CI
- Validate workflow files with actionlint
- Test on multiple Python versions
- Add coverage reporting
- Test pre-commit hooks work

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-08 | Test all 4 configs in matrix | Ensures every combination validated |
| 2025-01-08 | Verify test counts | Catches missing test conditionals |
| 2025-01-08 | Add validation script | Makes local testing easier |
| 2025-01-08 | Keep tests fast | Matrix runs in parallel, ~30s total |
| 2025-01-16 | Start implementation | Foundation complete, CI is next priority |

---

## Implementation Progress

### Current Session (2025-01-16)

**Starting Implementation:**
- Following 5-step workflow from .rules
- Step 1: Context gathered ✅
- Step 2: Documenting plan in this scratchpad
- Step 3: Will pitch approach and wait for approval
- Step 4: Implementation (create workflow, validation script, docs)
- Step 5: Document completion and verify

**Why Goal 05 First:**
1. Just completed manual verification (346 tests) - time to automate!
2. Prevents regressions before adding new features (Goals 06/07)
3. Foundation work enables safe iteration
4. High ROI - 2-3 hours investment, permanent protection
5. Catches template issues before users hit them

**Implementation Order:**
1. Create `.github/workflows/test-template.yml` with matrix strategy
2. Create `scripts/validate-template.sh` for local testing
3. Update `README.md` with testing documentation
4. Update `CONTRIBUTING.md` with development guidelines
5. (Optional) Add pre-commit hook for Jinja syntax validation
6. Add CI status badge to README

**Next Step:** Pitch approach to user and wait for approval before implementation.