# Quick Start — AI Session Guide

> Read this when starting a new AI session on an existing project.
> Time to context: <2 minutes.

---

## Step 1: Boot
```
Send BOOT.md to your AI assistant
→ System auto-reads: CLAUDE.md, INDEX.md, state.json, today.md
→ Outputs Status Report
```

## Step 2: Orient (if context is unclear)
```
/context
→ Reads context-map.md
→ Shows: project phase, current task, recent decisions
→ Suggests: "Continue from [X]?"
```

## Step 3: Work
```
/status                     → Quick status check
/task [description]         → Create new task
/agent [name] [request]     → Direct an agent
/done [task-id]             → Complete a task
/commit                     → Commit with verification gate
```

## Step 4: End Session
```
Update memory/hot/today.md → Handoff section
Update memory/hot/context-map.md → Current Position
```

---

## Common Workflows

| I want to... | Do this |
|-------------|---------|
| Start a brand new project | `/idea [description]` |
| Onboard existing codebase | `/onboard [path]` |
| **Hackathon 48h (phòng IT bằng prompt)** | Đọc `docs/onboarding/HUONG-DAN-SU-DUNG.md` → điền brief → `/hackathon` |
| Add a feature | `/task [feature description]` |
| Fix a bug | `/agent [relevant-agent] fix [bug description]` |
| Review architecture | `/agent cto review [area]` |
| Check project health | `/status` |
| End the sprint | `/sprint-end` |
