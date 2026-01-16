# Goal 06: Add Template Variants

## Status: ⚪ Not Started

**Created:** 2025-01-08
**Updated:** 2025-01-08
**Priority:** Medium
**Estimated Effort:** 3-4 hours
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