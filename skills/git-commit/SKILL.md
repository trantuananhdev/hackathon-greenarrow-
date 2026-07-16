# Skill: git-commit — Commit Pipeline

**Trigger:** Agent reports "done" | `/commit` | `/done [task-id]`
**Never skip** — no matter how small the task.

---

## Pipeline (mandatory order)

### Step 1 — Verify Gate (run BEFORE commit)

```bash
# In order — stop immediately on failure
[project lint command]          # Zero new warnings (not zero total)
[project test command]          # All tests pass
[project build command]         # Clean build

# For DB migration:
[migrate status command]        # Confirm migration state
[integration test command]      # Pass after migration
```

> ⛔ **Any step fails = DO NOT commit.**
> Report specific error. Do not use `--no-verify`. Do not "assume it passes".

### Step 2 — Review Diff

```bash
git diff --staged
```

Checklist:
```
□ No console.log / debugger / TODO: delete
□ No hardcoded secret / API key
□ No .env file
□ No files outside task scope
□ Breaking change? → need ADR first
```

### Step 3 — Commit

```bash
git commit -m "[type]([scope]): [subject]

[body if needed]

Closes: [task-id]
Sprint: S[N]"
```

### Step 4 — Push + Move Task

```bash
git push origin [branch-name]

# Move task file
# tasks/active/[id].json → tasks/done/[id].json

# Update task result in file
{
  "status": "done",
  "result": {
    "commit_hash": "[git rev-parse --short HEAD]",
    "verify_passed": true,
    "done_at": "[timestamp]"
  }
}
```

### Step 5 — Update State

```
# Update memory/hot/state.json
# task_counts.active -= 1
# task_counts.done_this_sprint += 1
# next_action → next highest priority task

# Update memory/hot/context-map.md
# Current Position → next task
```

---

## Output

```
✅ Committed: [abc1234]
📝 "[type](scope): subject"
🌿 Branch: [branch-name]
📋 Task [id] → moved to tasks/done/

⚡ Next: [id] — [next task description]
```

---

## Error Cases

| Situation | Action |
|-----------|--------|
| Test fails | List which tests fail, don't commit, suggest fix |
| Lint error | Show errors, suggest auto-fix if available, wait for confirm |
| Nothing staged | Check `git status`, may have forgotten `git add` |
| Push rejected | Pull rebase first: `git pull --rebase origin [branch]` |
| Build fails | Show full error, don't guess the fix |
| Merge conflict | STOP, don't auto-resolve important conflicts |
