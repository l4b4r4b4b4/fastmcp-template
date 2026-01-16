# Contributing to FastMCP Template

Thank you for your interest in contributing to the FastMCP Cookiecutter Template! This guide will help you get started with template development.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/l4b4r4b4b4/fastmcp-template
cd fastmcp-template

# Install dependencies (for testing)
uv sync

# Test template generation
uv run cookiecutter . --no-input
```

## Template Structure

This is a **Cookiecutter template repository**, meaning:
- The template files live in `{{cookiecutter.project_slug}}/`
- Configuration is in `cookiecutter.json`
- Post-generation hooks are in `hooks/`
- Template repo files (this README, CI, etc.) are at the root

### Key Files

| File | Purpose |
|------|---------|
| `cookiecutter.json` | Template configuration options |
| `{{cookiecutter.project_slug}}/` | Template files (become generated project) |
| `hooks/post_gen_project.py` | Post-generation setup (git init, dependencies, etc.) |
| `.github/workflows/test-template.yml` | CI testing for template |
| `scripts/validate-template.sh` | Local validation script |
| `VERIFICATION.md` | Manual verification report |

## Testing Your Changes

### Before Submitting a PR

**Required:**

1. **Test locally** - Verify your changes work:
   ```bash
   # Quick test one configuration
   ./scripts/validate-template.sh minimal
   
   # Or test all configurations (recommended)
   ./scripts/validate-template.sh --all
   ```

2. **Check CI** - Ensure CI passes on your PR

3. **Update docs** - If you changed behavior, update README/docs

**Optional but recommended:**

4. **Manual testing** - Generate a project and use it:
   ```bash
   uv run cookiecutter . --output-dir /tmp/test
   cd /tmp/test/<project-name>
   uv run pytest
   uv run <project-slug> stdio
   ```

### Testing Script

The `validate-template.sh` script runs the same checks as CI:

```bash
# Test specific configuration
./scripts/validate-template.sh minimal       # 74 tests
./scripts/validate-template.sh full          # 101 tests  
./scripts/validate-template.sh demos-only    # 86 tests
./scripts/validate-template.sh secrets-only  # 85 tests

# Test everything
./scripts/validate-template.sh --all
```

Each test:
1. Generates a project with cookiecutter
2. Runs pytest (and verifies test count)
3. Runs ruff linting
4. Checks for hardcoded values (Goal 01 regression)

## Making Changes

### Adding a New Configuration Option

1. **Update `cookiecutter.json`:**
   ```json
   {
     "include_my_feature": ["no", "yes"]
   }
   ```

2. **Add Jinja2 conditionals in template files:**
   ```python
   {% if cookiecutter.include_my_feature == "yes" %}
   # Your feature code
   {% endif %}
   ```

3. **Update tests** if needed (conditional test blocks)

4. **Update expected test counts** in:
   - `.github/workflows/test-template.yml`
   - `scripts/validate-template.sh`

5. **Update documentation:**
   - README.md (configuration options table)
   - VERIFICATION.md (if new config combinations)

6. **Test all configurations:**
   ```bash
   ./scripts/validate-template.sh --all
   ```

### Modifying Template Files

When editing files in `{{cookiecutter.project_slug}}/`:

1. **Use Jinja2 variables:**
   ```python
   # Good
   name="{{ cookiecutter.project_name }}"
   
   # Bad
   name="fastmcp-template"  # Hardcoded!
   ```

2. **Test for hardcoded values:**
   ```bash
   # CI checks for these automatically
   grep -r "fastmcp-template" {{cookiecutter.project_slug}}/
   grep -r "l4b4r4b4b4" {{cookiecutter.project_slug}}/
   ```

3. **Conditional blocks for optional features:**
   ```python
   {% if cookiecutter.include_demo_tools == "yes" %}
   from app.tools.demo import hello
   {% endif %}
   ```

### Updating Test Counts

If you add/remove tests in the template, update expected counts:

**1. Find new test counts:**
```bash
# Generate each config and count tests
for config in minimal full demos-only secrets-only; do
  ./scripts/validate-template.sh $config 2>&1 | grep "Test count"
done
```

**2. Update `.github/workflows/test-template.yml`:**
```yaml
matrix:
  config:
    - name: minimal
      expected_tests: 74  # Update this
```

**3. Update `scripts/validate-template.sh`:**
```bash
declare -A CONFIGS=(
  ["minimal"]="no:no:74"  # Update third value
```

**4. Update `VERIFICATION.md`** if doing full re-verification

## CI Workflow

### What CI Tests

The `test-template.yml` workflow runs on every push/PR and tests:

1. **All 4 configurations** (minimal, full, demos-only, secrets-only)
2. **Project generation** succeeds
3. **All tests pass** in generated projects
4. **Test count matches** expected count
5. **Linting passes** (ruff check)
6. **No hardcoded values** (fastmcp-template, l4b4r4b4b4)

### CI Matrix

```yaml
strategy:
  fail-fast: false
  matrix:
    config:
      - name: minimal
        demo_tools: "no"
        secret_tools: "no"
        expected_tests: 74
      # ... (3 more configs)
```

Each configuration runs in parallel, taking ~2-3 minutes total.

### If CI Fails

1. **Check the workflow logs** in GitHub Actions
2. **Reproduce locally:**
   ```bash
   ./scripts/validate-template.sh <config-that-failed>
   ```
3. **Fix the issue** and push again
4. **CI will re-run** automatically

## Pull Request Checklist

Before submitting your PR:

- [ ] Tested locally with `./scripts/validate-template.sh --all`
- [ ] All 4 configurations generate successfully
- [ ] Tests pass in generated projects
- [ ] No hardcoded template values
- [ ] Updated documentation (README, VERIFICATION, etc.)
- [ ] Updated test counts if tests added/removed
- [ ] CI passes on your branch

## Code Style

### Template Files

- Follow the generated project's style (see `{{cookiecutter.project_slug}}/.rules`)
- Use Jinja2 variables for all dynamic content
- Keep conditionals readable (indent, comment complex logic)

### Template Repo Files

- Bash scripts: Follow ShellCheck recommendations
- YAML: Valid syntax, clear naming
- Markdown: Clear headings, code blocks with language tags

## Getting Help

- **Issues**: https://github.com/l4b4r4b4b4/fastmcp-template/issues
- **Discussions**: https://github.com/l4b4r4b4b4/fastmcp-template/discussions
- **Documentation**: [VERIFICATION.md](VERIFICATION.md) for testing details

## Thank You! 🎉

Your contributions help make this template better for everyone. We appreciate your time and effort!