# Goal 04: Enforce CI-Gated Workflow

## Status: 🟢 Complete

**Created:** 2025-01-08
**Updated:** 2025-01-08 (Completed)
**Priority:** High
**Estimated Effort:** 2-3 hours (Actual: ~1.5 hours)
**Depends On:** 
- ✅ Goal 01 (Fix Cookiecutter Templating) - Complete
- ✅ Goal 02 (Fix Demo Tools Test Consistency) - Complete
- ✅ Goal 03 (Add Minimal Tools Option) - Complete

---

## Objective

Ensure that generated repositories enforce a strict CI-gated workflow where release, publish, and deploy workflows **cannot run** unless CI has passed. The workflow should enforce:

1. **Feature branch** (branched from latest main)
2. **Stage → Pre-commit hooks** (local validation)
3. **Push → PR → CI** (remote validation)
4. **Merge → Release/Publish/Deploy** (only after CI passes)

---

## Current State Analysis

### What's Already Working ✅

| Component | Status | Notes |
|-----------|--------|-------|
| **CI Workflow** | ✅ Excellent | Runs on PR and push to main, has ci-success job |
| **Pre-commit hooks** | ✅ Good | Includes `no-commit-to-branch` for main |
| **Release → CI gate** | ✅ Excellent | Uses `workflow_run` with proper CI check |
| **CD → Release gate** | ✅ Excellent | Uses `workflow_run`, waits for Release |
| **Publish → Release gate** | ⚠️ Indirect | Triggers on release event (manual step after CI/Release) |
| **Tag push handling** | ✅ Good | Tag pushes trigger Release, but no explicit CI verification |

### Current Workflow Analysis

After examining the actual workflow files, the situation is **better than expected**:

#### Release Workflow (release.yml) - Lines 41-54
```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]
  
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
      - "v[0-9]+.[0-9]+.[0-9]+-*"
  
  workflow_dispatch:
```

**Current State:**
- ✅ Has `workflow_run` trigger for post-CI builds
- ✅ Has `check-ci` job that verifies CI conclusion
- ⚠️ Tag pushes trigger independently (potential bypass)
- ✅ Has logic to check CI status (lines 84-110)

**Key Finding:** The workflow already checks `github.event.workflow_run.conclusion == 'success'` but tag pushes are a separate event path.

#### Publish Workflow (publish.yml) - Lines 19-21
```yaml
on:
  release:
    types: [published]
```

**Current State:**
- ⚠️ Triggers on `release.published` event
- ❌ No explicit CI or Release workflow verification
- ✅ Uses PyPI trusted publishing (secure)
- ℹ️ Manual step: user creates release after images built

**Reality:** This is a **manual gate** - users must:
1. Wait for CI to pass
2. Wait for Release workflow to build images
3. Manually create GitHub Release
4. Then Publish workflow runs

This is actually safer than automation, but lacks explicit enforcement.

#### CD Workflow (cd.yml) - Lines 43-47
```yaml
on:
  workflow_run:
    workflows: ["Release"]
    types: [completed]
    branches: [main]
```

**Current State:**
- ✅ Waits for Release workflow to complete
- ✅ Properly gated behind Release
- ✅ No issues found

---

## Research Findings

### Actual Workflow Chain (Current)

The current implementation already has most protections in place:

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT PHASE                            │
├─────────────────────────────────────────────────────────────────┤
│  1. Feature Branch → Commit → Push                               │
│  2. Pre-commit hooks enforce local checks                        │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Open PR → CI Runs (lint, test, security)                    │
│  4. CI must pass (enforced by branch protection)                │
│  5. Merge to main                                                │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. CI re-runs on main                                           │
│  7. ✅ Release workflow waits for CI via workflow_run            │
│  8. ✅ check-ci job verifies CI success                          │
│  9. Docker images built and pushed to GHCR                       │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  10. User manually creates GitHub Release                        │
│  11. ⚠️ Publish workflow triggers (no explicit verification)     │
│  12. Package published to PyPI                                   │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  13. ✅ CD workflow waits for Release via workflow_run           │
│  14. Deploy to staging/production                                │
└─────────────────────────────────────────────────────────────────┘

**Tag Push Path (Potential Bypass):**
```
Tag push (v0.0.1) → Release workflow → check-ci job
                      ↓
                   Checks event type but doesn't verify CI for tag
```
```

---

## Proposed Solution

After analysis, the current implementation is **mostly correct**. Only minor improvements needed:

### Issues to Address

1. **Tag push doesn't explicitly verify CI** - Could push tag before CI passes
2. **Publish workflow has no Release verification** - Manual step relies on user discipline
3. **Pre-commit missing --unsafe-fixes** - Inconsistent with .rules
4. **Branch protection not documented** - Users don't know how to set up repo

### Implementation Plan

#### Task 01: Add Explicit CI Verification for Tag Pushes ✅

**Change:** Add CI status check to `check-ci` job when triggered by tag push.

**Location:** `release.yml` lines 84-110 (check-ci job)

**Implementation:**
```yaml
- name: Verify CI passed for tag pushes
  if: github.event_name == 'push' && github.ref_type == 'tag'
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    echo "Tag push detected - verifying CI passed for commit"
    gh api repos/${{ github.repository }}/commits/${{ github.sha }}/check-runs \
      --jq '.check_runs[] | select(.name == "CI Success") | .conclusion' \
      | grep -q "success" || {
        echo "ERROR: CI has not passed for this commit"
        echo "Please ensure CI passes before pushing version tags"
        exit 1
      }
```

**Why:** Prevents releasing images from commits that haven't passed CI.

**Result:** ✅ Added verification step in release.yml check-ci job (lines 97-121)

#### Task 02: Add Release Workflow Verification to Publish ✅

**Change:** Add job to verify Release workflow completed successfully before publishing.

**Location:** `publish.yml` - add new job before `publish`

**Implementation:**
```yaml
verify-release:
  name: Verify Release Completed
  runs-on: ubuntu-latest
  if: github.event_name == 'release'
  steps:
    - name: Check Release workflow status
      uses: actions/github-script@v7
      with:
        script: |
          const { data: runs } = await github.rest.actions.listWorkflowRuns({
            owner: context.repo.owner,
            repo: context.repo.repo,
            workflow_id: 'release.yml',
            head_sha: context.sha,
          });
          const releaseRun = runs.workflow_runs.find(
            run => run.conclusion === 'success'
          );
          if (!releaseRun) {
            core.setFailed('Release workflow has not completed successfully');
          }
```

**Why:** Ensures Docker images were built before publishing to PyPI.

**Result:** ✅ Added verify-release job in publish.yml, build job depends on it

#### Task 03: Update Pre-commit with --unsafe-fixes ✅

**Change:** Add `--unsafe-fixes` to Ruff pre-commit hook.

**Location:** `.pre-commit-config.yaml`

**Current:**
```yaml
- id: ruff
  args: [--fix, --exit-non-zero-on-fix]
```

**New:**
```yaml
- id: ruff
  args: [--fix, --unsafe-fixes, --exit-non-zero-on-fix]
```

**Why:** Aligns with .rules requirement for --unsafe-fixes.

**Result:** ✅ Updated .pre-commit-config.yaml line 11

#### Task 04: Document Branch Protection Setup ✅

**Change:** Add branch protection documentation to CONTRIBUTING.md.

**Location:** `CONTRIBUTING.md` - new section

**Content:**
- Required branch protection rules
- Status checks to require
- Setup instructions
- Screenshots/examples

**Why:** Users need guidance on proper repository configuration.

**Result:** ✅ Added comprehensive section to CONTRIBUTING.md (lines 318-406)

#### Task 05: Add Workflow Chain Diagram ✅

**Change:** Add visual diagram showing workflow dependencies.

**Location:** `README.md` or `CONTRIBUTING.md`

**Content:**
- ASCII or Mermaid diagram
- Show: CI → Release → Publish → CD
- Highlight manual steps
- Note branch protection requirements

**Why:** Helps users understand the full release process.

**Result:** ✅ Added CI/CD workflow diagram to README.md (lines 258-302)

---

## Acceptance Criteria

- [x] Tag pushes fail if CI hasn't passed for the commit
- [x] Publish workflow verifies Release workflow completed successfully
- [x] Pre-commit hooks include `--unsafe-fixes` flag
- [x] CONTRIBUTING.md documents branch protection rules
- [x] README.md or CONTRIBUTING.md has workflow chain diagram
- [x] Documentation clear and comprehensive
- [x] All changes applied to template (not individual projects)

---

## Files to Modify

| File | Changes | Status |
|------|---------|--------|
| `.github/workflows/release.yml` | Added CI verification step for tag pushes (25 lines) | ✅ Complete |
| `.github/workflows/publish.yml` | Added verify-release job with GitHub API check (39 lines) | ✅ Complete |
| `.pre-commit-config.yaml` | Added `--unsafe-fixes` to Ruff args | ✅ Complete |
| `CONTRIBUTING.md` | Added 88-line branch protection section with workflow chain | ✅ Complete |
| `README.md` | Added 46-line CI/CD workflow diagram section | ✅ Complete |

---

## Key Insights from Research

### What's Already Good ✅

1. **Release workflow already uses workflow_run** - Properly waits for CI on main branch merges
2. **check-ci job exists** - Already has logic to check CI conclusion
3. **CD properly chained to Release** - No issues found
4. **Manual release step is intentional** - Provides human gate before PyPI publish
5. **Security scanning in place** - Trivy scans both base and app images

### What Needs Improvement ⚠️

1. **Tag push path lacks CI verification** - Can push v0.0.1 tag before CI passes
2. **Publish workflow trusts user judgment** - No automated check that Release succeeded
3. **Pre-commit inconsistent with .rules** - Missing --unsafe-fixes flag
4. **Setup documentation missing** - Users don't know about branch protection

### Why Current Design is Mostly Correct

The manual release creation step is actually a **feature, not a bug**:
- Gives developers control over when to publish
- Allows for release note preparation
- Prevents accidental publishes on every merge
- Still requires CI to pass (via branch protection)
- Still requires Release to complete (Docker images built)

We just need to make the implicit checks **explicit** in the workflows.

---

## Security Considerations

1. **Workflow permissions** - Ensure `workflow_run` has correct permissions
2. **Token scope** - CI status checks require `checks:read` permission
3. **Branch protection bypass** - Admins can bypass; document this risk
4. **Tag protection** - Consider tag protection rules to prevent unauthorized tags

---

## Implementation Notes

- Release workflow already has robust `check-ci` job - just needs tag push verification
- GitHub's `workflow_run` only triggers for default branch - this is why tag pushes are separate
- The `ci-success` job in CI workflow is designed exactly for this use case
- Pre-commit config is in template root, applies to generated projects
- Branch protection must be configured per-repository (can't be in template)
- Consider adding `.github/settings.yml` for Probot Settings app to auto-configure repos

## Verification Plan

After implementation, test these scenarios:

| Scenario | Expected Behavior | Test Method |
|----------|------------------|-------------|
| Push tag before CI passes | Release workflow fails at check-ci | Push tag on feature branch |
| Push tag after CI passes | Release workflow succeeds | Merge PR, wait for CI, push tag |
| Create release manually | Publish runs and checks Release status | Create release via GitHub UI |
| Merge without CI | Blocked by branch protection | Try to merge with failing CI |
| workflow_dispatch | Succeeds regardless | Manual trigger button |

---

## Implementation Summary

**Changes Made:**

1. **Release Workflow Enhancement** - Added 25-line verification step
   - Queries GitHub API for CI status when tag pushed
   - Fails with clear error message if CI hasn't passed
   - Provides guidance on correct workflow

2. **Publish Workflow Gate** - Added 39-line verify-release job
   - Uses GitHub Actions API to check Release workflow status
   - Prevents PyPI publish without Docker images
   - Build job depends on verification

3. **Pre-commit Alignment** - Single-line change
   - Added `--unsafe-fixes` flag to Ruff
   - Now consistent with .rules requirements

4. **Branch Protection Documentation** - 88-line comprehensive section
   - Step-by-step setup instructions
   - Required status checks listed
   - Workflow chain diagram included
   - Testing instructions provided

5. **README CI/CD Section** - 46-line workflow diagram
   - Visual ASCII diagram of full process
   - Key safeguards highlighted
   - Manual gates identified

**Total Lines Changed:** ~198 lines across 5 files

**Impact:**
- ✅ No breaking changes to existing workflows
- ✅ Defensive checks added, not flow changes
- ✅ Manual steps intentionally preserved
- ✅ Clear documentation for users

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-08 | Use tag verification over blocking | Maintains current workflow, minimal changes |
| 2025-01-08 | Add Release verification to Publish | Ensures Docker images built before PyPI publish |
| 2025-01-08 | Document branch protection | Can't enforce via workflow, needs repo settings |
| 2025-01-08 | Keep manual release creation | Provides intentional gate, allows release note prep |
| 2025-01-08 | Add inline verification vs restructure | Defensive additions, not architectural changes |