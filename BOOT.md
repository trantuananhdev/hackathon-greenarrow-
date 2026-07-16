# BOOT.md — v4 Autonomous Boot

> **Send this file only. The entire system self-starts.**
> Principle: Read the minimum — do the maximum.

---

## ⚡ Boot Sequence (4 files, ~10KB total)

```
1. Read: CLAUDE.md              ← Core constitution (immutable)
2. Read: INDEX.md               ← Full system map
3. Read: memory/hot/state.json  ← Current state machine
4. Read: memory/hot/today.md    ← Today's session context
```

> **STOP. Do not read anything else during boot.**
> Load additional files only when a specific task requires them.
> Consult `INDEX.md` to find what file lives where.

---

## 📊 Status Report (AI outputs this after boot)

```
## 🚀 System Ready — v4

🏗️ Phase:   [from state.json → project_phase.current]
🎯 Sprint:  [from state.json → current_sprint.goal]
⚡ Active:  [N tasks — count files in tasks/active/, do NOT read them]
🚧 Blocked: [N tasks — count files in tasks/blocked/]
📍 Next:    [from state.json → next_action]
🧠 Memory:  hot([this week]) / warm([N patterns]) / cold(archive)
🌿 Branch:  [git branch --show-current if available]
📍 Context: [from state.json → context_breadcrumb.last_task_touched]

Agents ready: cto · pm · tech-lead · fe · be · ai · qa · security
```

---

## ⚡ Quick Commands

| Command | Action |
|---------|--------|
| `/status` | Reload state.json + today.md → report |
| `/idea [description]` | Start ideation pipeline → CTO Agent |
| `/design [feature]` | Create system design → CTO Agent |
| `/task [description]` | Create task in `tasks/active/` |
| `/done [task-id]` | Verify → move to `tasks/done/` |
| `/block [task-id] [reason]` | Move to `tasks/blocked/` |
| `/load [name]` | Lazy-load specific file via INDEX.md |
| `/commit [msg]` | Run git-commit skill |
| `/adr [title]` | Create new ADR + update INDEX |
| `/sprint-end` | Trigger session-end skill → archive + prune |
| `/agent [name] [request]` | Activate a specific agent |
| `/learn [insight]` | Write to memory/hot/today.md → promote at sprint-end |
| `/context` | Show context map — where is the project right now? |
| `/onboard [project-path]` | Auto-init new project into this system |
| `/hackathon` | Hackathon 48h pipeline — SSOT `WORKFLOW.md` |
| `/review` | Tech Lead reviews current work |

---

## 🧠 Memory Load Strategy

```
ALWAYS load (boot):
  memory/hot/state.json        ← <2KB, current state machine
  memory/hot/today.md          ← session context

LOAD ON DEMAND (when task requires):
  memory/hot/context-map.md    ← when context is unclear
  tasks/active/[id].json       ← only when working on that task
  goals/current/quarter.md     ← when needing OKR context
  goals/current/sprint.md      ← when creating/reviewing tasks
  architecture/PROJECT.md      ← when writing/reviewing code
  architecture/ENV-MAP.md      ← when using services/env vars
  architecture/system-design/  ← when designing new features
  memory/warm/patterns/        ← when encountering similar problems
  architecture/adr/[id].md     ← when needing decision context
  docs/PRD/[feature].md        ← when implementing a feature
  docs/RFC/[topic].md          ← when evaluating a proposal

NEVER load at boot:
  tasks/done/                  ← only for retrospective
  tasks/backlog/               ← only for grooming
  goals/archive/               ← only for historical research
  memory/cold/                 ← only for long-term research
```

---

## 🚨 Hard Rules (no exceptions)

1. **Do not load files you don't need** — context is a precious resource, don't waste it
2. **Do not claim done without verify** — run the command, read the output
3. **Do not commit code that hasn't passed gate** — gate defined in `skills/git-commit/SKILL.md`
4. **Do not modify accepted ADRs** — create a new ADR to supersede
5. **Do not update state.json and task files asynchronously** — update together
6. **Sprint-end is mandatory** — never close a sprint without running `/sprint-end`
7. **Update context-map.md after every significant action** — future sessions depend on it
8. **When receiving a new project, run project-onboarding skill first** — don't start coding blind
