# GIT-WORKFLOW.md — Automated Git Workflow

> AI READS THIS when performing git operations. All commits, branches, PRs must follow this.
> Do not invent formats — look them up here.

---

## 🌿 Branch Strategy

```
main          ← Production. Only merge via reviewed PR.
├── develop   ← Integration branch. Features merge here.
│   ├── feat/[task-id]-[short-description]
│   ├── fix/[task-id]-[short-description]
│   ├── chore/[task-id]-[short-description]
│   └── docs/[task-id]-[short-description]
└── hotfix/[issue-id]-[short-description]  ← Production bugs only
```

### Create Branch (AI does this)
```bash
# Format: [type]/[task-id]-[short-description]
git checkout -b feat/S1-03-user-api
git checkout -b fix/BL-001-memory-flush-bug
git checkout -b chore/S1-05-update-deps
```

**Rules:**
- Always branch from `develop` (not `main`)
- Short names, kebab-case, starts with task-id
- One branch = one task (never combine tasks)
- Delete branch after merge

---

## 📝 Commit Convention (Conventional Commits)

```
[type]([scope]): [subject]

[body - optional]

[footer - optional]
```

### Types
| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Refactor without adding feature or fixing bug |
| `test` | Add/modify tests |
| `chore` | Build, dependencies, config |
| `perf` | Performance improvement |
| `ci` | CI/CD config |
| `revert` | Revert previous commit |

### Scope (project-specific, examples)
`auth`, `user`, `payment`, `api`, `db`, `ui`, `infra`, `agent`, `memory`

### Examples
```bash
# ✅ Correct
git commit -m "feat(memory): add goals/ folder hierarchy with 4-tier structure"
git commit -m "fix(agent): prevent hallucination when active-tasks.json empty"
git commit -m "docs(architecture): add PROJECT.md and GIT-WORKFLOW.md"
git commit -m "test(skills): add unit tests for verification-before-completion"
git commit -m "chore(deps): upgrade sdk to v0.24"

# Breaking change
git commit -m "feat(api)!: change response format for /tasks endpoint

BREAKING CHANGE: response.data is now paginated object instead of array
Migration guide: see docs/migrations/v2.md"

# ❌ Wrong
git commit -m "fix bug"
git commit -m "update code"
git commit -m "WIP"
git commit -m "done"
```

---

## 🔄 Pull Request Process

### PR Template (AI fills this)
```markdown
## Summary
<!-- 1-2 sentences: what and why -->

## Changes
- [ ] [Main change 1]
- [ ] [Main change 2]

## Task Link
Closes: [task-id from active tasks]
Sprint: [Sprint N from goals/sprint.md]

## Test Coverage
- Unit tests: [ ] Added / [ ] Updated / [ ] N/A
- Integration tests: [ ] Added / [ ] Updated / [ ] N/A
- Manual test steps:
  1. [Step 1]
  2. [Step 2]

## Verify Gate
```bash
# Command for reviewer to verify
[test command]
[build command]
```

## Breaking Changes
[ ] Yes → describe and link migration guide
[x] No

## ADR
[ ] New ADR needed (create before merge)
[x] Not needed
```

### Merge Rules
1. **Self-review first** — re-read diff, no typos
2. **CI must be green** — never merge with failing tests
3. **Squash merge** — clean history on develop
4. **Delete branch** — after merge

---

## 🏷️ Versioning (Semantic Versioning)

```
MAJOR.MINOR.PATCH
  │     │     └── Bug fix, non-breaking
  │     └──────── New feature, backward compatible
  └────────────── Breaking change
```

### Auto-tag (AI does this after merge to main)
```bash
# After successful deploy
git tag -a v1.2.3 -m "Release v1.2.3: [sprint N] - [sprint goal]"
git push origin v1.2.3
```

### CHANGELOG.md (AI updates this)
```markdown
## [1.2.3] - 2026-01-15
### Added
- feat: ...
### Fixed
- fix: ...
### Changed
- refactor: ...
```

---

## 🛡️ Protected Rules (AI must never violate)

1. **No direct push to `main` or `develop`**
2. **No committing `console.log`, debug code, or hardcoded secrets**
3. **No committing `.env` files** (only `.env.example`)
4. **No force push** unless explicitly requested
5. **No merge PR when CI is red**
6. **No skipping pre-commit hooks**

---

## ⚡ Pre-commit Checklist (AI checks before every commit)

```bash
# AI runs in this order:
□ 1. [lint command]       # No new warnings
□ 2. [test command]       # All pass
□ 3. [build command]      # Build succeeds
□ 4. git diff --staged    # Final review
□ 5. git commit -m "[conventional format]"
```

---

*Related ADRs: `architecture/adr/` | Updated: [date]*
