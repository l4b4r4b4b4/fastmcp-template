# Goal 08: Zed Project-Specific Thread Storage

> Configure Zed editor to store conversation threads in project-specific locations

---

## Status: ⚪ Not Started

**Created:** 2026-01-19
**Priority:** Low
**Estimated Effort:** 1-2 hours
**Depends On:** None

---

## Objective

Configure the generated projects to store Zed editor conversation threads within the project's `.agent/` directory rather than Zed's global location. This keeps AI conversation context project-specific and version-controllable.

---

## Problem Description

By default, Zed stores conversation threads globally in `~/.config/zed/conversations/` (or similar). This means:

- ❌ Conversations are not project-specific
- ❌ Context is lost when switching between projects
- ❌ Cannot version control conversation history with the project
- ❌ Team members don't share conversation context
- ❌ Project-specific knowledge is scattered across global storage

---

## Proposed Solution

Configure Zed's settings to store threads in a project-local directory:

```json
// .zed/settings.json
{
  "assistant": {
    "conversation_storage": ".agent/threads"
  }
}
```

This would:
- ✅ Keep conversations alongside project code
- ✅ Allow version control of important conversations (optional)
- ✅ Maintain context across sessions for the same project
- ✅ Enable team sharing of conversation history

---

## Research Required

### Questions to Answer

1. **Does Zed support project-local thread storage?**
   - Check Zed documentation for `assistant` settings
   - Review Zed source code if needed
   - Test with current Zed version

2. **What settings are available?**
   - `conversation_storage` path configuration
   - Thread format and structure
   - Privacy/encryption considerations

3. **What are the implications?**
   - Git ignore patterns needed?
   - Size considerations for large thread histories
   - Conflict resolution if multiple users

---

## Implementation Plan

### Task 1: Research Zed Settings

- [ ] Check Zed documentation for assistant/conversation settings
- [ ] Identify available configuration options
- [ ] Test if project-local storage is supported
- [ ] Document findings

### Task 2: Update .zed/settings.json Template

**File:** `{{cookiecutter.project_slug}}/.zed/settings.json`

**Current content (abbreviated):**
```json
{
  "lsp": { ... },
  "file_scan_exclusions": [ ... ]
}
```

**Add assistant configuration (if supported):**
```json
{
  "assistant": {
    "conversation_storage": ".agent/threads",
    "default_model": "claude-sonnet-4-20250514"
  }
}
```

### Task 3: Create Threads Directory

**Add to template:**
```
{{cookiecutter.project_slug}}/
└── .agent/
    └── threads/
        └── .gitkeep
```

### Task 4: Update .gitignore

**File:** `{{cookiecutter.project_slug}}/.gitignore`

**Add options:**
```gitignore
# Zed conversation threads (uncomment to track)
# .agent/threads/

# Or ignore all threads (default - privacy)
.agent/threads/*.json
```

### Task 5: Document the Feature

**Update README or create THREADS.md:**
- Explain the thread storage location
- How to version control threads (optional)
- Privacy considerations
- How to share with team

---

## Acceptance Criteria

- [ ] Research complete: Zed settings documented
- [ ] `.zed/settings.json` updated with thread storage config (if supported)
- [ ] `.agent/threads/` directory created in template
- [ ] `.gitignore` updated with appropriate patterns
- [ ] Documentation explains the feature
- [ ] Generated projects have correct configuration

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `{{cookiecutter.project_slug}}/.zed/settings.json` | Update | Add assistant config |
| `{{cookiecutter.project_slug}}/.agent/threads/.gitkeep` | Create | Placeholder for threads |
| `{{cookiecutter.project_slug}}/.gitignore` | Update | Add thread patterns |
| `{{cookiecutter.project_slug}}/README.md` | Update | Document feature |

---

## Alternatives Considered

### Alternative 1: Keep Global Storage
- **Pros:** No configuration needed, Zed default
- **Cons:** Loses project context, not shareable

### Alternative 2: Symlink Approach
- **Pros:** Works with any Zed version
- **Cons:** Complex setup, platform-specific

### Alternative 3: Manual Thread Export
- **Pros:** User controls what's saved
- **Cons:** Extra work, easy to forget

**Decision:** Prefer native Zed configuration if supported, otherwise document best practices.

---

## Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Zed doesn't support this | High | Medium | Research first, document alternatives |
| Large thread files | Low | Low | Add to .gitignore by default |
| Privacy concerns | Medium | Low | Document and provide .gitignore |

---

## Notes

- This is a low-priority enhancement
- Depends on Zed's feature set
- May become more valuable as AI assistants become more integrated
- Could be expanded to support other editors (VS Code, Cursor, etc.)

---

## References

- [Zed Editor Documentation](https://zed.dev/docs)
- [Zed Settings Reference](https://zed.dev/docs/configuring-zed)
- [Zed Assistant Documentation](https://zed.dev/docs/assistant)
- Current `.zed/settings.json` in template

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-19 | Created goal | Improve project-specific AI context |
| 2026-01-19 | Set as Low priority | Nice-to-have, not critical |
| 2026-01-19 | Research-first approach | Don't assume Zed supports this |