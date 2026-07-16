# Skill: context-recovery — Recover When Lost

**Trigger:** `/context` | New session starts | AI is confused about project state | "Where was I?"
**Goal:** In <30 seconds, know exactly where the project stands and what to do next.

---

## When to Use

```
✅ Use when:
- Starting a new AI session on an existing project
- Feeling confused about project state
- After a long break from the project
- Context window is getting full, need to re-orient
- Human asks "where are we?" or "what's the status?"

❌ Do NOT use for:
- First-time project setup (→ use project-onboarding skill)
```

---

## Recovery Protocol

```
/context
    │
    ▼
Step 1: Read state.json (~1KB)
    → project_phase, sprint status, task counts, next_action
    → context_breadcrumb: last agent, last task, last file
    │
    ▼
Step 2: Read context-map.md (~1KB)
    → Project position, current task, context chain
    → "Must Remember" items
    → Recent decisions
    │
    ▼
Step 3: Count files (no content reading)
    → ls tasks/active/ → count active tasks
    → ls tasks/blocked/ → count blocked tasks
    │
    ▼
Step 4: Quick git check
    → git branch --show-current
    → git status --short
    → git log -1 --oneline
    │
    ▼
Step 5: Output structured context report
```

---

## Context Report Format

```
## 🗺️ Context Recovery — [timestamp]

### Project Position
🏗️ Phase: [ideation/design/planning/development/testing/deployment]
🎯 Sprint: S[N] — "[sprint goal]" — day [X/14]
📊 Tasks: [A] active · [B] blocked · [D] done this sprint

### Where We Left Off
📍 Last task: [S#-##] — [description]
🤖 Last agent: [agent name]
📁 Last file: [file path]
💡 Last decision: [description]
🌿 Branch: [branch name]
📝 Last commit: [hash] — [message]

### What Needs Attention
🔴 Blockers: [list any blocked tasks with reasons]
⚡ Next action: [from state.json → next_action]

### Context Chain (full picture)
1. Mission: [1 sentence]
2. Quarter OKR: [relevant OKR]
3. Sprint Goal: [1 sentence]
4. Current Work: [what was being done]

### Suggestion
→ Continue with: [specific suggestion based on state]
→ Or type /status for full system report
```

---

## Recovery Depth Levels

### Level 1: Quick Orient (default /context)
- Read only: state.json + context-map.md
- Time: <10 seconds
- Use when: Brief pause, same session

### Level 2: Full Recovery (when Level 1 isn't enough)
- Read: state.json + context-map.md + today.md + sprint.md
- Scan: tasks/active/ (read task titles, not full content)
- Time: <30 seconds
- Use when: New session, need full picture

### Level 3: Deep Recovery (when completely lost)
- Read: All of Level 2 + quarter.md + PROJECT.md
- Read: Active task files in detail
- Check: git log -5
- Time: <60 seconds
- Use when: Long break, major confusion, new AI session on unfamiliar project

---

## After Recovery

```
1. Update session start in state.json → session.started
2. Confirm focus with human: "I see we were working on [X]. Continue?"
3. If human confirms → load relevant task file and resume
4. If human redirects → update context-map.md and start new focus
```

---

## Integration

- Reads: `memory/hot/state.json`, `memory/hot/context-map.md`, `memory/hot/today.md`
- Optionally reads: `goals/current/sprint.md`, `tasks/active/` (titles only)
- Updates: `state.json → session.started`, `context-map.md` if corrections needed
- Never modifies: task files, goals, architecture (read-only during recovery)
