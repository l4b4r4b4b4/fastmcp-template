# Task 02: Restructure Repository for Cookiecutter

**Status:** 🟢 Complete
**Priority:** High
**Created:** 2025-01-08
**Completed:** 2025-01-08
**Effort:** 1-2 hours
**Actual:** 30 minutes

---

## Objective

Restructure the fastmcp-template repository to follow Cookiecutter's standard layout by moving all template files into a `{{cookiecutter.project_slug}}/` directory. Only the template goal (`00-Template-Goal`) should be included in generated projects; development goals remain at repository root.

---

## Research & Context

### Cookiecutter Directory Structure

Standard Cookiecutter templates use this structure:

```
template-repo/                          # Repository root
├── cookiecutter.json                   # Template configuration ✓
├── hooks/                              # Generation hooks
│   ├── pre_gen_project.py
│   └── post_gen_project.py
├── {{cookiecutter.project_slug}}/      # TEMPLATE DIRECTORY (gets copied)
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   ├── README.md
│   └── ...                             # All project files
└── .agent/                             # Development artifacts (NOT copied)
    ├── scratchpad.md
    └── goals/
        ├── 01-*/                       # Development goal (excluded)
        ├── 02-*/                       # Development goal (excluded)
        └── ...
```

**Key Principle:** Only contents of `{{cookiecutter.project_slug}}/` are copied to generated projects.

### What Gets Included in Template

**Include (move to `{{cookiecutter.project_slug}}/`):**
- `app/` - Application code
- `tests/` - Test suite
- `docker/` - Docker configurations
- `.github/` - GitHub workflows
- `.agent/goals/00-Template-Goal/` - Template for users' goals
- `pyproject.toml`, `README.md`, `LICENSE`, etc.
- `.gitignore`, `.pre-commit-config.yaml`
- `.zed/settings.json`, `flake.nix`, `docker-compose.yml`

**Exclude (keep at repository root):**
- `cookiecutter.json` - Template configuration
- `hooks/` - Generation scripts
- `.agent/scratchpad.md` - Our development notes
- `.agent/goals/01-*`, `.agent/goals/02-*` - Our development goals
- `.git/` - Repository metadata

### Directory Name Must Be Variable

The directory name `{{cookiecutter.project_slug}}` is itself a Jinja2 template. When Cookiecutter runs:
1. User provides `project_name: "Weather API"`
2. Cookiecutter computes `project_slug: "weather-api"`
3. Template directory `{{cookiecutter.project_slug}}/` becomes `weather-api/`
4. Contents are copied into `weather-api/`

---

## Implementation Plan

### Step 1: Create Template Directory

```bash
mkdir -p "{{cookiecutter.project_slug}}"
```

Note: The literal directory name has double curly braces - this is correct!

### Step 2: Move Core Application Files

```bash
# Move application code
mv app/ "{{cookiecutter.project_slug}}/"

# Move tests
mv tests/ "{{cookiecutter.project_slug}}/"

# Move Docker configurations
mv docker/ "{{cookiecutter.project_slug}}/"

# Move GitHub workflows
mv .github/ "{{cookiecutter.project_slug}}/"
```

### Step 3: Move Configuration Files

```bash
# Project configuration
mv pyproject.toml "{{cookiecutter.project_slug}}/"
mv uv.lock "{{cookiecutter.project_slug}}/"

# Documentation
mv README.md "{{cookiecutter.project_slug}}/"
mv CONTRIBUTING.md "{{cookiecutter.project_slug}}/"
mv LICENSE "{{cookiecutter.project_slug}}/"

# Development tools
mv .pre-commit-config.yaml "{{cookiecutter.project_slug}}/"
mv .gitignore "{{cookiecutter.project_slug}}/"
mv docker-compose.yml "{{cookiecutter.project_slug}}/"
mv flake.nix "{{cookiecutter.project_slug}}/"
mv .envrc "{{cookiecutter.project_slug}}/"  # If exists
```

### Step 4: Move Editor Configurations

```bash
# Zed editor settings
mv .zed/ "{{cookiecutter.project_slug}}/"
```

### Step 5: Move Template Goal Only

```bash
# Create .agent structure in template
mkdir -p "{{cookiecutter.project_slug}}/.agent/goals"

# Copy only the template goal
cp -r .agent/goals/00-Template-Goal/ "{{cookiecutter.project_slug}}/.agent/goals/"
```

### Step 6: Create Repository-Level README

Create a new `README.md` at repository root explaining how to use the template:

```markdown
# FastMCP Cookiecutter Template

Generate production-ready FastMCP servers with RefCache integration.

## Usage

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template
```

See [template README]({{cookiecutter.project_slug}}/README.md) for features.
```

### Step 7: Verify Structure

After restructuring:

```
fastmcp-template/                       # Repository root
├── cookiecutter.json                   # Template config
├── README.md                           # How to use this template
├── {{cookiecutter.project_slug}}/      # Template directory
│   ├── .agent/
│   │   └── goals/
│   │       └── 00-Template-Goal/      # Only template goal
│   ├── app/
│   ├── tests/
│   ├── docker/
│   ├── .github/
│   ├── pyproject.toml
│   ├── README.md                       # Project README (will be templated)
│   └── ...
└── .agent/                             # Development (NOT in template)
    ├── scratchpad.md
    └── goals/
        ├── 01-*/
        └── 02-*/
```

---

## Files to Create/Modify

- [x] Create `{{cookiecutter.project_slug}}/` directory
- [x] Move `app/` to template directory (git mv)
- [x] Move `tests/` to template directory (git mv)
- [x] Move `docker/` to template directory (git mv)
- [x] Move `.github/` to template directory (git mv)
- [x] Move config files (pyproject.toml, uv.lock, flake.nix, etc.) to template directory (git mv)
- [x] Move `.zed/` to template directory (git mv)
- [x] Copy `.agent/goals/00-Template-Goal/` to template directory (cp -r)
- [x] Create new repository-level `README.md` (created)
- [x] Verify `.git/` remains at root (✓)
- [x] Verify `.agent/goals/01-*` and `02-*` remain at root (✓)
- [x] Move all documentation files (CHANGELOG.md, CONTRIBUTING.md, LICENSE, TOOLS.md, docs/)

---

## Testing Strategy

1. **Verify directory structure** - Check that template directory exists with correct name
2. **Verify file locations** - All project files are in template directory
3. **Verify exclusions** - Development goals NOT in template directory
4. **Test with cookiecutter** - Run `cookiecutter . --no-input` to verify structure
5. **Check generated project** - Verify generated project has correct structure

---

## Acceptance Criteria

- [x] `{{cookiecutter.project_slug}}/` directory exists at repository root
- [x] All application code moved to template directory (app/, tests/)
- [x] All configuration files moved to template directory (pyproject.toml, docker-compose.yml, etc.)
- [x] Only `00-Template-Goal` included in template's `.agent/goals/`
- [x] Development goals (01-*, 02-*) remain at repository root
- [x] Repository-level README.md created with Cookiecutter usage instructions
- [x] Structure matches Cookiecutter conventions
- [x] Git history preserved for all moved files (used `git mv`)
- [ ] Can run `cookiecutter . --no-input` without errors (blocked - needs Task 03 Jinja2 conversion)

---

## Risks & Mitigation

### Risk 1: Breaking git history
**Mitigation:** Use `git mv` instead of `mv` to preserve file history

### Risk 2: Broken relative paths
**Mitigation:** Will be fixed in Task 03 when adding Jinja2 templates

### Risk 3: Missing files
**Mitigation:** Use `git status` to verify all tracked files are accounted for

---

## Notes

- The directory name `{{cookiecutter.project_slug}}` is literal - don't substitute it yet!
- This is just restructuring - no Jinja2 templating yet (that's Task 03)
- After this task, the repository will look "weird" but that's expected for Cookiecutter
- Don't worry about imports/paths yet - those will be templated in Task 03

---

## Completion Log

### 2025-01-08 - Restructuring Complete ✅

**What Was Done:**

1. **Created template directory structure**
   - Created `{{cookiecutter.project_slug}}/` directory at repository root

2. **Moved all project files using `git mv`** (preserves history)
   - Application: `app/`, `tests/`
   - Docker: `docker/`, `docker-compose.yml`
   - Config: `pyproject.toml`, `uv.lock`, `flake.nix`, `flake.lock`
   - GitHub: `.github/`
   - Editor: `.zed/`
   - Development: `.gitignore`, `.pre-commit-config.yaml`, `.python-version`
   - Documentation: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `TOOLS.md`, `docs/`

3. **Copied template goal**
   - Copied `.agent/goals/00-Template-Goal/` to template directory
   - Development goals (01-*, 02-*) remain at repository root (excluded from generated projects)

4. **Created repository-level README.md**
   - New README explaining how to use the Cookiecutter template
   - Usage examples, feature list, project structure
   - Links to template directory's README for generated project docs

5. **Verified structure**
   ```
   fastmcp-template/
   ├── cookiecutter.json                 # Template config
   ├── README.md                          # How to use template
   ├── {{cookiecutter.project_slug}}/     # Template directory (40 files)
   │   ├── .agent/goals/00-Template-Goal/ # Only template goal
   │   ├── app/                           # All app code
   │   ├── tests/                         # All tests
   │   ├── docker/                        # Docker configs
   │   ├── .github/                       # Workflows
   │   └── ...                            # All project files
   └── .agent/                            # Development (NOT copied)
       └── goals/
           ├── 01-*/                      # Excluded
           └── 02-*/                      # Excluded
   ```

6. **Git status check**
   - All moves detected as renames (R) - history preserved ✓
   - 43+ files successfully restructured
   - New files added: repository README.md, template .agent structure

**Known Issue:**
- Template generation fails because files in template directory still have:
  - GitHub Actions syntax: `${{ github.repository_owner }}`
  - Other template placeholders that need Jinja2 conversion
- **Resolution:** Task 03 will convert all files to proper Jinja2 templates

**Next Steps:**
- Task 03: Convert files to Jinja2 templates (escape GitHub Actions syntax, add cookiecutter variables)
- Then test: `cookiecutter . --no-input` should work

**Metrics:**
- Files moved: 43
- Directories moved: 7
- Git history preserved: 100%
- Time taken: 30 minutes (vs estimated 1-2 hours)