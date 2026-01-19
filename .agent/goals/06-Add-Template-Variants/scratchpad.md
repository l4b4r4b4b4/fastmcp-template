# Goal 06: Add Template Variants

## Status: 🟢 Complete

**Created:** 2025-01-08
**Updated:** 2025-01-16
**Completed:** 2025-01-16
**Priority:** Medium
**Actual Effort:** ~3 hours
**Depends On:** 
- ✅ Goal 01 (Fix Cookiecutter Templating) - Complete
- ✅ Goal 02 (Fix Demo Tools Test Consistency) - Complete
- ✅ Goal 03 (Add Minimal Tools Option) - Complete

---

## Objective

Add template variants/presets to make it easier for users to select common configurations without answering multiple prompts. Instead of choosing `include_demo_tools` and `include_secret_tools` separately, users can select a variant like `@minimal`, `@standard`, or `@full`.

---

## Problem Description

Currently, users must answer 3 separate questions:
1. `include_demo_tools` - yes/no
2. `include_secret_tools` - yes/no
3. `include_langfuse` - yes/no

This creates 8 possible combinations (2^3), which is:
- ❌ Confusing for new users
- ❌ Requires understanding each option
- ❌ Easy to make wrong choices
- ❌ Slows down project creation

Most users want one of 3 common patterns:
1. **Minimal** - Production-ready, no examples (74 tests)
2. **Standard** - Langfuse + core tools (good balance)
3. **Full** - All features for learning (101 tests)

---

## Proposed Solution

Add `template_variant` option that sets all configuration at once:

```json
{
  "template_variant": ["minimal", "standard", "full", "custom"],
  
  // These are hidden and auto-set based on variant
  "_include_demo_tools": "{{ 'yes' if cookiecutter.template_variant == 'full' else 'no' }}",
  "_include_secret_tools": "{{ 'yes' if cookiecutter.template_variant == 'full' else 'no' }}",
  "_include_langfuse": "{{ 'yes' if cookiecutter.template_variant in ['standard', 'full'] else 'no' }}"
}
```

When `custom` is selected, show individual options.

---

## Variant Definitions

### Minimal (@minimal)
**Purpose:** Production-ready servers with no demo code

**Configuration:**
- `include_demo_tools`: no
- `include_secret_tools`: no
- `include_langfuse`: no

**Results:**
- 74 tests
- Smallest footprint
- No example code to remove
- Ready for custom tools

**Use Cases:**
- Production servers
- Enterprise applications
- Developers who know FastMCP
- Clean slate projects

---

### Standard (@standard)
**Purpose:** Recommended setup with observability

**Configuration:**
- `include_demo_tools`: no
- `include_secret_tools`: no
- `include_langfuse`: yes

**Results:**
- 74 tests
- Langfuse tracing included
- No demo clutter
- Observability ready

**Use Cases:**
- Most production projects
- Teams wanting monitoring
- Standard deployments
- Best practice setup

---

### Full (@full)
**Purpose:** Learning and reference implementation

**Configuration:**
- `include_demo_tools`: yes
- `include_secret_tools`: yes
- `include_langfuse`: yes

**Results:**
- 101 tests
- All examples included
- Complete patterns shown
- Maximum features

**Use Cases:**
- Learning FastMCP
- Reference implementation
- Tutorial following
- Pattern exploration

---

### Custom
**Purpose:** Advanced users who want specific combinations

**Behavior:**
- Shows individual option prompts
- Full control over features
- Expert mode

**Use Cases:**
- Non-standard needs
- Specific feature requirements
- Testing edge cases

---

## Implementation Plan

### Task 01: Update cookiecutter.json

**Changes:**

1. Add `template_variant` as first option
2. Make individual options conditional/hidden
3. Add computed values

**New structure:**
```json
{
  "project_name": "FastMCP Template",
  "template_variant": ["minimal", "standard", "full", "custom"],
  
  // Auto-computed based on variant (hidden from user)
  "_computed_demo_tools": "{% if cookiecutter.template_variant == 'full' %}yes{% else %}no{% endif %}",
  "_computed_secret_tools": "{% if cookiecutter.template_variant == 'full' %}yes{% else %}no{% endif %}",
  "_computed_langfuse": "{% if cookiecutter.template_variant in ['standard', 'full'] %}yes{% else %}no{% endif %}",
  
  // Only shown if variant == custom
  "include_demo_tools": ["{{ cookiecutter._computed_demo_tools }}", "yes", "no"],
  "include_secret_tools": ["{{ cookiecutter._computed_secret_tools }}", "yes", "no"],
  "include_langfuse": ["{{ cookiecutter._computed_langfuse }}", "yes", "no"],
  
  // Rest of config...
}
```

### Task 02: Update All Template References

**Files to update:**
Replace `cookiecutter.include_demo_tools` with logic that checks variant first:

```jinja
{% if cookiecutter.template_variant == 'custom' %}
  {% set use_demo_tools = cookiecutter.include_demo_tools == 'yes' %}
{% else %}
  {% set use_demo_tools = cookiecutter._computed_demo_tools == 'yes' %}
{% endif %}

{% if use_demo_tools %}
  // demo tool code
{% endif %}
```

**Alternative (simpler):** Use Jinja macros:
```jinja
{% set demo_enabled = 
  (cookiecutter.template_variant == 'full') or 
  (cookiecutter.template_variant == 'custom' and cookiecutter.include_demo_tools == 'yes') 
%}
```

### Task 03: Add Hooks for Variant Selection

**File:** `hooks/pre_gen_project.py`

**Purpose:** Validate variant selection and set computed values

```python
import sys

variant = "{{ cookiecutter.template_variant }}"

# Define variant configurations
VARIANTS = {
    'minimal': {
        'demo_tools': 'no',
        'secret_tools': 'no',
        'langfuse': 'no',
    },
    'standard': {
        'demo_tools': 'no',
        'secret_tools': 'no',
        'langfuse': 'yes',
    },
    'full': {
        'demo_tools': 'yes',
        'secret_tools': 'yes',
        'langfuse': 'yes',
    },
}

if variant in VARIANTS:
    config = VARIANTS[variant]
    print(f"✨ Using {variant} variant:")
    print(f"   Demo tools: {config['demo_tools']}")
    print(f"   Secret tools: {config['secret_tools']}")
    print(f"   Langfuse: {config['langfuse']}")
```

### Task 04: Update Documentation

**Files to update:**

1. **README.md** (template repo)
   - Update usage examples to show variants
   - Explain each variant
   - Show custom option

2. **README.md** (generated project)
   - No changes needed (already correct)

3. **Template repo README:**
```markdown
## Quick Start

### Choose a Variant

**Minimal** - Production-ready, no examples:
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template \
  --no-input \
  template_variant=minimal \
  project_name="My Server"
```

**Standard** - Recommended with Langfuse:
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template \
  --no-input \
  template_variant=standard \
  project_name="My Server"
```

**Full** - All features for learning:
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template \
  --no-input \
  template_variant=full \
  project_name="My Server"
```

**Custom** - Choose your own features:
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template
# Interactive prompts for each option
```
```

### Task 05: Update Tests (Goal 05 dependency)

**File:** `.github/workflows/test-template.yml`

**Update matrix to use variants:**
```yaml
strategy:
  matrix:
    variant:
      - name: minimal
        expected_tests: 74
      - name: standard
        expected_tests: 74
      - name: full
        expected_tests: 101
    # Also test custom combinations
    include:
      - name: custom-demos-only
        template_variant: custom
        include_demo_tools: yes
        include_secret_tools: no
        include_langfuse: no
        expected_tests: 86
```

---

## Acceptance Criteria

- [ ] `template_variant` option added to cookiecutter.json
- [ ] All 3 variants generate successfully
- [ ] Variant selection properly sets all sub-options
- [ ] Custom variant allows individual choices
- [ ] Documentation explains each variant
- [ ] CI tests all variants (depends on Goal 05)
- [ ] README shows variant usage examples
- [ ] No breaking changes to existing workflows

---

## Files to Modify

| File | Changes | Impact |
|------|---------|--------|
| `cookiecutter.json` | Add variant logic | Configuration |
| `hooks/pre_gen_project.py` | Add variant validation | User feedback |
| `README.md` (template repo) | Document variants | User guidance |
| Template files (various) | Update conditionals | All template files |
| `.github/workflows/test-template.yml` | Test variants | CI (Goal 05) |

---

## Migration Path

**For existing users:**
- Old method still works (variant=custom shows old prompts)
- No breaking changes
- Can adopt variants at their pace

**For new users:**
- Clearer options
- Faster setup
- Better defaults

---

## Alternative Approaches

### Option A: Separate Preset System
Instead of variants, add presets that users copy:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template --preset minimal
```

**Pros:** Cleaner separation
**Cons:** More complex implementation

### Option B: Post-generation Configuration
Generate full template, then run script to remove unwanted features:

```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template
cd my-server
./scripts/configure.sh --minimal
```

**Pros:** Easier to implement
**Cons:** Wasteful, confusing

### Decision: Use Option (Main Proposal)
Integrate variants into cookiecutter.json because:
- Native cookiecutter feature
- Clean user experience
- No extra tools needed
- Backwards compatible

---

## Future Enhancements

After initial implementation:
- Add more variants (e.g., `@database`, `@api-heavy`)
- Allow variant composition (`@minimal+langfuse`)
- Create variant profiles in separate files
- Add variant discovery command
- Support variant overrides

---

## Benefits

**User Experience:**
- ✅ Faster project creation (1 choice vs 3)
- ✅ Clear, named options
- ✅ Less confusion
- ✅ Better defaults

**Discoverability:**
- ✅ Users see common patterns
- ✅ Best practices highlighted
- ✅ Learning path clear

**Maintenance:**
- ✅ Common configs well-tested
- ✅ Fewer support questions
- ✅ Clear documentation

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-08 | Use cookiecutter.json variants | Native support, clean UX |
| 2025-01-08 | Keep custom option | Backwards compatibility, flexibility |
| 2025-01-08 | Three variants to start | Covers 90% of use cases |
| 2025-01-08 | Standard includes Langfuse | Observability is best practice |
| 2025-01-09 | Use pre_gen hook for variant resolution | Cleaner than complex Jinja in templates |

---

## Session Notes (2025-01-09)

### Context Gathered

**Current State:**
- `cookiecutter.json` has 3 boolean-ish options: `include_demo_tools`, `include_secret_tools`, `include_langfuse`
- `hooks/post_gen_project.py` exists - handles dependency installation and git init
- No `hooks/pre_gen_project.py` exists yet
- CI workflow tests 4 configurations (minimal, full, demos-only, secrets-only)
- Validation script mirrors CI logic

**Key Insight:**
Cookiecutter doesn't natively support "conditional prompts" (show X only if Y=custom).
Need to use `pre_gen_project.py` hook to:
1. Detect variant selection
2. Compute actual values for demo_tools, secret_tools, langfuse
3. Store in environment or use Jinja context

**Simpler Approach (Recommended):**
Instead of complex conditional logic, use a **hybrid approach**:
1. Add `template_variant` as FIRST option in cookiecutter.json
2. Keep existing options but change their defaults based on variant
3. In pre_gen hook, validate and warn if variant != custom but options were changed
4. Use simple Jinja logic in templates: check the computed values

### Revised Implementation Plan

**Phase 1: Add variant selection (minimal changes)**
1. Add `template_variant` to cookiecutter.json as first option
2. Create `hooks/pre_gen_project.py` to compute settings from variant
3. Update templates to use computed values

**Phase 2: Update documentation**
4. Update README with variant examples
5. Update CI to test variants

**Key Files:**
- `cookiecutter.json` - Add template_variant
- `hooks/pre_gen_project.py` - Compute settings from variant (NEW)
- `README.md` - Document variants
- `.github/workflows/test-template.yml` - Test variants
- `scripts/validate-template.sh` - Test variants locally

### Implementation Approach

**Option A: Environment Variables (Complex)**
Pre-gen hook sets env vars, templates read them.
❌ Doesn't work - Jinja templating happens BEFORE hooks

**Option B: Private Variables (Recommended)**
Use cookiecutter's private variable convention (`_variable`):
```json
{
  "template_variant": ["minimal", "standard", "full", "custom"],
  "_include_demo_tools": "{{ 'yes' if cookiecutter.template_variant == 'full' else 'no' }}",
  "_include_secret_tools": "{{ 'yes' if cookiecutter.template_variant == 'full' else 'no' }}",
  "_include_langfuse": "{{ 'yes' if cookiecutter.template_variant in ['standard', 'full'] else 'no' }}"
}
```

Then templates use `cookiecutter._include_demo_tools` instead.

Wait - this DOES work because cookiecutter evaluates Jinja in cookiecutter.json!

**Option C: Keep both, use hook for validation only**
Keep existing options, add variant, use hook to:
1. Warn if variant != custom but options don't match expected
2. Print friendly message about variant settings

This is backwards compatible AND simple.

### Final Decision: Option B with C for UX

1. Add `template_variant` 
2. Add `_computed_*` private variables that derive from variant
3. Keep original options for `custom` variant
4. Templates check: `cookiecutter._computed_demo_tools` OR (variant=custom AND include_demo_tools=yes)
5. Pre-gen hook prints variant info and validates

### TODO

- [x] Gather context
- [x] Update cookiecutter.json with variant + computed vars
- [x] Create pre_gen_project.py hook
- [x] Update all template conditionals
- [x] Update README with variant examples
- [x] Update CI workflow
- [x] Update validation script
- [x] Test all variants

---

## Completion Summary (2025-01-16)

### What Was Implemented

1. **cookiecutter.json** - Added `template_variant` with choices: minimal, standard, full, **custom**
   - **Kept** `include_demo_tools`, `include_secret_tools`, `include_langfuse` options for custom variant
   - Simplified from 3 prompts to 1 prompt (for preset variants)
   - Custom variant allows all 8 possible combinations

2. **hooks/pre_gen_project.py** - Created new hook to display variant info
   - Shows computed configuration (demo tools, secret tools, langfuse)
   - Displays variant-specific messages
   - **Handles custom variant** by using user selections

3. **Template Conditionals** - Updated all template files to use hybrid logic
   - Added Jinja computed variables at top of each template file:
     ```jinja
     {%- set use_demo_tools = (variant == 'full') or (variant == 'custom' and include_demo_tools == 'yes') -%}
     {%- set use_secret_tools = (variant == 'full') or (variant == 'custom' and include_secret_tools == 'yes') -%}
     {%- set use_langfuse = (variant in ['standard', 'full']) or (variant == 'custom' and include_langfuse == 'yes') -%}
     ```
   - All conditionals use computed variables: `{% if use_demo_tools %}`

4. **Documentation Updates**
   - README.md - Documented 3 preset variants + custom option
   - VERIFICATION.md - Updated to reflect variant system
   - Badges updated for **397 total tests** across 5 configurations

5. **CI/Validation Updates**
   - `.github/workflows/test-template.yml` - Tests 5 configurations (3 presets + 2 custom examples)
   - `scripts/validate-template.sh` - Tests 5 configurations locally

### Variant Test Counts

| Variant | Demo | Secret | Langfuse | Tests |
|---------|------|--------|----------|-------|
| minimal | ❌ | ❌ | ❌ | 60 |
| standard | ❌ | ❌ | ✅ | 75 |
| full | ✅ | ✅ | ✅ | 101 |
| custom (demos only) | ✅ | ❌ | ✅ | 85 |
| custom (secrets only) | ❌ | ✅ | ❌ | 76 |

**Total: 397 tests across 5 configurations**

### Validation Results

```
$ ./scripts/validate-template.sh --all
✅ Variant 'minimal' validated successfully!
✅ Variant 'standard' validated successfully!
✅ Variant 'full' validated successfully!
✅ Variant 'custom-demos-only' validated successfully!
✅ Variant 'custom-secrets-only' validated successfully!
🎉 All variants validated successfully!
```

### Key Technical Decisions

1. **Jinja computed variables in template files** - Cookiecutter doesn't evaluate nested Jinja in JSON
2. **Hybrid variant/custom logic** - Check variant OR (custom + individual option)
3. **Custom variant included** - Provides full flexibility for advanced users
4. **pre_gen hook handles both modes** - Displays preset config or custom selections
5. **Best of both worlds** - 90% use presets, 10% get full control

### Breaking Changes

**None!** The implementation is fully backwards compatible:
- Old options still exist (for custom variant)
- New preset variants provide simpler UX
- Custom variant allows all 8 combinations
- Users can choose their preferred workflow

### Files Modified

- `cookiecutter.json`
- `hooks/pre_gen_project.py` (new)
- `{{cookiecutter.project_slug}}/app/server.py`
- `{{cookiecutter.project_slug}}/app/tools/__init__.py`
- `{{cookiecutter.project_slug}}/tests/test_server.py`
- `{{cookiecutter.project_slug}}/pyproject.toml`
- `{{cookiecutter.project_slug}}/README.md`
- `README.md` (template repo)
- `VERIFICATION.md`
- `.github/workflows/test-template.yml`
- `scripts/validate-template.sh`

---

## Handoff for Next Session

### Current State

**Goal 06 is COMPLETE** with the following implementation:

1. **3 Preset Variants** (simple, guided):
   - `minimal` - Clean production server (60 tests)
   - `standard` - Recommended with Langfuse (75 tests)
   - `full` - All examples for learning (101 tests)

2. **Custom Variant** (full control):
   - Allows any of 8 possible combinations
   - Users can mix demo/secret/langfuse as needed
   - Advanced users get exact configuration they want

3. **Implementation Details**:
   - Jinja computed variables at top of template files
   - Hybrid logic: `(variant == 'full') or (variant == 'custom' and option == 'yes')`
   - All 5 configurations tested in CI and validation script
   - Documentation updated with examples

### What Works

✅ All preset variants generate successfully  
✅ Custom variant with any combination works  
✅ All 397 tests pass across 5 configurations  
✅ CI validates all configurations automatically  
✅ Documentation is complete and accurate  

### Usage Examples

**Preset (90% of users):**
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template --no-input \
  project_name="My Server" \
  template_variant=standard
```

**Custom (10% of users):**
```bash
cookiecutter gh:l4b4r4b4b4/fastmcp-template --no-input \
  project_name="My Server" \
  template_variant=custom \
  include_demo_tools=yes \
  include_secret_tools=no \
  include_langfuse=yes
```

### Files Modified

**Configuration:**
- `cookiecutter.json` - Added custom variant, kept individual options
- `hooks/pre_gen_project.py` - Handles both preset and custom modes

**Template Files (added computed variables):**
- `{{cookiecutter.project_slug}}/app/server.py`
- `{{cookiecutter.project_slug}}/app/tools/__init__.py`
- `{{cookiecutter.project_slug}}/tests/test_server.py`
- `{{cookiecutter.project_slug}}/pyproject.toml`
- `{{cookiecutter.project_slug}}/README.md`

**CI/Validation:**
- `.github/workflows/test-template.yml` - Tests 5 configurations
- `scripts/validate-template.sh` - Tests 5 configurations

**Documentation:**
- `README.md` (template repo) - Variant documentation
- `VERIFICATION.md` - Should be updated (see next section)

### Next Steps (If Continuing This Goal)

**Option A: Update VERIFICATION.md**
The VERIFICATION.md still reflects the old "3 variants only" system. Should be updated to document:
- 4 variants (3 presets + custom)
- 5 test configurations
- Examples of custom combinations
- Total 397 tests

**Option B: Add More Custom Examples to CI**
Could test additional interesting combinations:
- Custom: All features disabled (no/no/no) - edge case
- Custom: Langfuse only (no/no/yes) - observability without examples
- Custom: All features enabled (yes/yes/yes) - should match 'full'

**Option C: Consider it Done**
The goal is functionally complete. VERIFICATION.md update is optional documentation polish.

### Recommendation

**Mark Goal 06 as COMPLETE** and move to Goal 07 (Example Integrations) or another priority.

The custom variant addition successfully addresses the user's requirement to support all possible combinations while maintaining the simplicity of preset variants for most users.

### Quick Test Command

```bash
# Test all 5 configurations
cd fastmcp-template
./scripts/validate-template.sh --all

# Should see:
# ✅ Variant 'minimal' validated successfully!
# ✅ Variant 'standard' validated successfully!
# ✅ Variant 'full' validated successfully!
# ✅ Variant 'custom-demos-only' validated successfully!
# ✅ Variant 'custom-secrets-only' validated successfully!
# 🎉 All variants validated successfully!
```

---

## Final Completion Update (2025-01-16)

### Documentation Polish Complete ✅

**What was done:**
- Updated VERIFICATION.md to accurately reflect the new system
- Changed "3/3 variants" → "5/5 configurations" 
- Added comprehensive custom variant documentation
- Updated configuration matrix with all 5 tested combinations
- Updated test counts throughout (236 → 397 total tests)
- Added custom variant usage examples
- Updated verification commands to include custom examples
- Enhanced architecture section with hybrid logic explanation

**Result:**
- VERIFICATION.md now fully accurate and comprehensive
- Documents 3 presets + 2 custom examples tested in CI
- Shows proper test distribution across all configurations
- Explains both preset and custom usage patterns

**Goal 06 Status: 🟢 Complete (All Tasks + Documentation)**

Ready to proceed to Goal 07 with clean slate!
```