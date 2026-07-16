# Skill: session-end — Sprint Wrap-up

**Trigger:** `/sprint-end` | End of sprint | Human requests sprint close
**Goal:** Clean up, archive, prune, prepare for next sprint.
After this skill: system is clean, context is fresh, next sprint is ready.

---

## Pipeline (execute in order)

### Phase 1 — Verify & Close Tasks (5 min)

```bash
# 1. List all tasks still in tasks/active/
ls tasks/active/

# 2. For each task:
#    - Has commit hash? If not → verify before closing
#    - Done → move to tasks/done/
#    - Not done → decide: carry over or backlog?
```

Ask human:
```
Sprint S[N] ending. [N] tasks still incomplete:
- [S#-##]: [name] — carry over to S[N+1]? or backlog?
```

### Phase 2 — Retrospective

Update `goals/current/sprint.md`:
```markdown
### 🔁 Sprint Retrospective
**Velocity:** [X/Y points]
**Start doing:** [...]
**Stop doing:** [...]
**Continue doing:** [...]
**Patterns recorded:** [N new]
**ADRs created:** [N]
```

### Phase 3 — Memory Prune + Promote

**Hot → Warm (promote if valuable):**
```
Read memory/hot/today.md and session notes
→ Find insights that appeared 2+ times or are especially valuable
→ Promote to memory/warm/patterns/[topic].md
→ Remove from hot after promoting
```

**Warm → Cold (demote if stale):**
```
Read memory/warm/patterns/ list
→ Which patterns were NOT used this sprint?
→ If unused for 2 consecutive quarters → move to memory/cold/[YYYY-Q#]/
```

**Hot reset:**
```
# Reset today.md for new sprint
# Don't delete state.json — update it
```

### Phase 4 — Archive Goals

```bash
# Archive current sprint
mkdir -p goals/archive/[YYYY-Q#]/
# Move goals/current/sprint.md → goals/archive/[YYYY-Q#]/sprint-[N].md

# Create new sprint file from template
```

### Phase 5 — Update State + Commit

```bash
# Update state.json
{
  "current_sprint": { "id": "S[N+1]", "goal": "[TBD — needs grooming]" },
  "task_counts": { "active": [N carried over], "done_this_sprint": 0 },
  "memory_health": { "last_prune": "[today]", "next_prune": "[+2 weeks]" }
}

# Commit system state
git add memory/ goals/ tasks/done/
git commit -m "chore(sprint): close S[N], prepare S[N+1]

Sprint S[N] summary:
- Completed: [X/Y] tasks, [P] points
- Carried over: [N] tasks
- Patterns learned: [N]
- ADRs created: [N]"
```

---

## Output

```
✅ Sprint S[N] closed

📊 Results:
- Completed: [X/Y tasks] | [P points]
- Carry over: [N tasks] → S[N+1]
- New patterns: [N] → warm/patterns/
- ADRs created: [N]

🧹 Memory:
- Promoted to warm: [N insights]
- Demoted to cold: [N stale patterns]
- Hot memory reset ✓

📁 Archive:
- goals/archive/[YYYY-Q#]/sprint-[N].md ✓
- tasks/done/ has [N] completed tasks ✓

⚡ Sprint S[N+1] ready
Need to groom backlog before starting.
```
