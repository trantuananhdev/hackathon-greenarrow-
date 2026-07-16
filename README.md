# claude-code-workflow v4

> AI-first autonomous development system. Stack-agnostic. Self-governing.
> **Send `BOOT.md` only — the entire system self-starts.**

---

## What's New in v4

| v3 Problem | v4 Solution |
|-----------|-------------|
| Starts at task level — no ideation flow | **Full pipeline:** idea → system design → PRD → plan → code |
| Only orchestrator (overloaded role) | **3-layer agents:** CTO + PM + Tech Lead + 5 executors |
| No document system | **Complete docs/:** PRD, RFC, runbooks, API docs, onboarding |
| Manual project onboarding (fill 4-5 files) | **Auto-onboarding:** scan project → generate scaffolding |
| Context tracking only at sprint level | **Context map:** always know where the project is |
| No inter-agent communication protocol | **File-based messaging:** structured agent-to-agent protocol |
| Stack-specific templates (TypeScript assumed) | **Stack-agnostic:** adapts to any technology |
| Missing QA + Security agent specs | **8 complete agent definitions** with clear boundaries |

---

## 6 Core Principles

```
1. INDEXED       — Consult index first, read file second
2. TIERED        — Memory has TTL, never grows unbounded
3. STATE-DRIVEN  — File movement = state transition
4. LAZY-LOADED   — Load when needed, never preemptively
5. SELF-PRUNING  — Sprint-end auto-cleans, archives, promotes
6. CONTEXT-AWARE — Always know where the project is, never get lost
```

---

## Agent Architecture

```
HUMAN (Product Owner)
  │  /idea, /approve
  ▼
CTO Agent ──────── Strategy Layer
  │                (System design · ADR · Tech strategy · Risk review)
  ▼
PM Agent ────────── Planning Layer
Tech Lead Agent ──┘ (PRD · Roadmap · Sprint · Task breakdown · Code review)
  │
  ▼  tasks/active/*.json
┌─────────────────── Execution Layer ───────────────────┐
│ FE Agent    BE Agent    AI Agent    QA Agent           │
│ UI·CSS·UX   API·DB      LLM·RAG    Test·Verify·Gate   │
└───────────────────────────────────────────────────────┘
  │
  ▼  read/write markdown files
FILE SYSTEM — Single Source of Truth
```

---

## Quick Structure

```
claude-code-workflow-v4/
├── BOOT.md              # Send this — system boots
├── CLAUDE.md            # Immutable constitution
├── INDEX.md             # Navigation map
│
├── memory/
│   ├── hot/             # state.json + today.md + context-map.md
│   ├── warm/            # patterns/ + decisions/
│   └── cold/            # archive
│
├── tasks/
│   ├── active/          # 1 file = 1 active task
│   ├── done/            # Completed tasks
│   ├── blocked/         # Blocked tasks
│   └── backlog/         # Waiting to be picked
│
├── goals/
│   ├── current/         # mission + quarter + sprint (always = "now")
│   └── archive/         # Past quarters
│
├── architecture/
│   ├── PROJECT.md       # Stack, conventions (stack-agnostic template)
│   ├── GIT-WORKFLOW.md  # Branch, commit, PR rules
│   ├── ENV-MAP.md       # Services, ports, env vars
│   ├── adr/             # Architecture Decision Records
│   └── system-design/   # System design documents
│
├── docs/
│   ├── PRD/             # Product Requirement Docs
│   ├── RFC/             # Proposals / Request for Comments
│   ├── runbooks/        # Operational procedures
│   ├── api/             # API documentation
│   └── onboarding/      # Quick start + project setup guides
│
├── agents/              # 8 specialized agents
│   ├── cto.md           # Strategy
│   ├── pm.md            # Planning
│   ├── tech-lead.md     # Planning
│   ├── fe.md / be.md    # Execution
│   ├── ai.md / qa.md    # Execution
│   └── security.md      # Cross-cutting
│
├── skills/              # 10 reusable skills
│   ├── ideation-to-plan/    # 🔑 Idea → Design → Plan
│   ├── project-onboarding/  # 🔑 Auto-init project
│   ├── context-recovery/    # 🔑 Recover when lost
│   ├── hackathon-sprint/    # 🚀 48h: WORKFLOW.md pipeline
│   ├── git-commit/          # Commit pipeline
│   ├── verification/        # Verify before done
│   └── ...
│
├── rules/               # Behavioral rules + protocols
└── commands/            # Slash commands
```

---

## How to Use

### Start a new project from scratch
```
1. /idea I want to build [system description]
   → CTO analyzes → creates system design + ADRs
   → PM creates PRD + roadmap + sprint plan
   → Tech Lead breaks down tasks
   → Human reviews & approves
   → Execution begins

2. Provide business/technical documents if available
   → System maps them into docs/PRD/ and architecture/
```

### Onboard an existing project
```
/onboard [path-to-project]
→ Scans directory → detects tech stack
→ Generates PROJECT.md, ENV-MAP.md
→ Creates initial mission.md prompt
→ System ready in <5 minutes
```

### Hackathon 48h (Đề bài → Enter → hệ thống hoàn thành)
```
1. Đọc docs/onboarding/HUONG-DAN-SU-DUNG.md   ← hướng dẫn master
2. Điền docs/PRD/hackathon-brief.md
3. Điền architecture/PROJECT.md (stack + lệnh test thật)
4. /hackathon  (hoặc copy Prompt trong WORKFLOW.md → Enter)
5. Review → /hackathon-approve → lặp BA→CTO→Tech Lead
6. Assign → /hackathon-go → DEV paste Prompt Phase 7 **một lần**
7. /done → AI auto-next task → Enter/"tiếp" đến TRACK COMPLETE
```
Cheat sheet: `HACKATHON-DAY.md` · Prompts: `WORKFLOW.md` · Chi tiết: `HACKATHON-GUIDE.md`


### Daily workflow
```
/status                    → Where are we?
/task [description]        → Create a task
/agent be Build user API   → Direct agent work
/done S1-02                → Verify + close task
/commit                    → Commit with gate
```

### End of sprint
```
/sprint-end
→ Archive → prune memory → retrospective → prepare next sprint
```

---

## Setup New Project (Manual)

1. Copy this folder into your project root
2. Fill `goals/current/mission.md` — why does this project exist
3. Fill `goals/current/quarter.md` — this quarter's OKRs
4. Fill `architecture/PROJECT.md` — tech stack + conventions
5. Fill `architecture/ENV-MAP.md` — services + env vars
6. Send `BOOT.md` to your AI assistant

**Or use `/onboard` to auto-generate steps 2-5.**
