# INDEX.md — Full System Map v4

> **AI uses this file to navigate — never read blindly.**
> Before reading any file, consult this INDEX to confirm the file exists and is worth reading.

---

## 🗺️ System Structure

```
claude-code-workflow-v4/
│
├── BOOT.md                           # Entry point — load only 4 files at boot
├── CLAUDE.md                         # Immutable constitution (read once)
├── INDEX.md                          # This file — navigation map
├── README.md                         # How to use this system
├── WORKFLOW.md                       # 🚀 SSOT hackathon 48h — copy prompt từng phase
├── HACKATHON-DAY.md                  # Cheat sheet ngày thi (trỏ về WORKFLOW)
├── architecture.md                   # 🚀 Core platform (hackathon) — đọc cùng design phases
│
├── memory/                           # Memory layer — tiered by TTL
│   ├── hot/                          # TTL: 1 week — always fresh
│   │   ├── state.json                # 🔴 CRITICAL: current state, sprint, next action
│   │   ├── today.md                  # Today's session log / scratchpad
│   │   └── context-map.md            # 🔴 WHERE IS THE PROJECT RIGHT NOW
│   ├── warm/                         # TTL: 1 quarter — patterns & decisions
│   │   ├── patterns/                 # Reusable lessons learned
│   │   │   └── [topic].md            # e.g., api-patterns.md, db-patterns.md
│   │   └── decisions/                # Decision log (not big enough for ADR)
│   │       └── [YYYY-MM].md
│   └── cold/                         # Archive — read only for research
│       └── [YYYY-Q#]/
│
├── tasks/                            # 1 file = 1 task
│   ├── active/                       # Currently working — read only when doing that task
│   │   └── [S#-##].json
│   ├── done/                         # Completed this sprint
│   │   └── [S#-##].json
│   ├── blocked/                      # Blocked — needs human action
│   │   └── [S#-##].json
│   └── backlog/                      # Waiting to be picked for sprint
│       └── [BL-###].json
│
├── goals/                            # Goal state machine
│   ├── current/                      # Always = "right now"
│   │   ├── mission.md                # North star (changes <1x/year)
│   │   ├── quarter.md                # This quarter's OKRs
│   │   └── sprint.md                 # This sprint's goal (2 weeks)
│   └── archive/                      # Past — read only when needing context
│       └── [YYYY-Q#]/
│
├── architecture/                     # Project architecture
│   ├── PROJECT.md                    # Stack, folder structure, conventions
│   ├── GIT-WORKFLOW.md               # Branch, commit, PR rules
│   ├── ENV-MAP.md                    # Services, ports, env vars
│   ├── adr/                          # Architecture Decision Records
│   │   ├── INDEX.md                  # All ADR list
│   │   ├── ADR-TEMPLATE.md           # Template for new ADRs
│   │   └── ADR-[NNN]-[slug].md       # Individual ADRs
│   └── system-design/                # System design documents
│       ├── TEMPLATE.md               # Template for new designs
│       └── [project-name].md         # Individual designs
│
├── docs/                             # Document system
│   ├── PRD/                          # Product Requirement Documents
│   │   ├── TEMPLATE.md
│   │   ├── hackathon-brief.md        # 🚀 INPUT: Đề bài từ BTC
│   │   └── hackathon-domain-pack.md  # 🚀 Phase 1 output
│   ├── design/                       # 🚀 Hackathon design + living indexes
│   │   ├── REPO-INDEX.md              # 🔑 Đang ở đâu / đọc gì / task board
│   │   ├── BE-INDEX.md                # 🔑 Backend folder + inventory + task map
│   │   ├── FE-INDEX.md                # 🔑 Frontend folder + inventory + task map
│   │   ├── AI-INDEX.md                # 🔑 Agent/RAG paths + task map
│   │   ├── hackathon-module-specs.md  # Phase 2
│   │   ├── hackathon-hl-design.md     # Phase 3 (+ folder structure FE/BE)
│   │   ├── hackathon-ll-design.md     # Phase 4 (+ file path map)
│   │   └── hackathon-impl-plan.md     # Phase 5
│   ├── RFC/                          # Request for Comments / Proposals
│   │   ├── TEMPLATE.md
│   │   └── [topic].md
│   ├── runbooks/                     # Operational runbooks
│   │   └── [procedure].md
│   ├── api/                          # API documentation
│   │   └── [service].md
│   └── onboarding/                   # Onboarding guides
│       ├── HUONG-DAN-SU-DUNG.md      # 🔑 MASTER: Đề bài → Enter → hoàn thành
│       ├── HACKATHON-GUIDE.md        # Step-by-step hackathon chi tiết
│       ├── QUICK-START.md
│       └── PROJECT-SETUP.md
│
├── agents/                           # Agent definitions — by layer
│   ├── cto.md                        # STRATEGY: System design, ADR, tech strategy
│   ├── pm.md                         # PLANNING: PRD, roadmap, sprint, OKR
│   ├── tech-lead.md                  # PLANNING: Task breakdown, code review, arch guard
│   ├── fe.md                         # EXECUTION: UI, components, CSS, UX
│   ├── be.md                         # EXECUTION: API, DB, services, infra
│   ├── ai.md                         # EXECUTION: LLM, prompts, pipelines, evals
│   ├── qa.md                         # EXECUTION: Test, verify, gate, report
│   └── security.md                   # CROSS-CUTTING: Auth review, vulnerability scan
│
├── skills/                           # Reusable skills
│   ├── git-commit/SKILL.md           # Commit pipeline with verify gate
│   ├── session-end/SKILL.md          # Sprint wrap-up + prune + promote
│   ├── agentic-execution/SKILL.md    # Multi-step AI task execution
│   ├── verification/SKILL.md         # Verify before claiming done
│   ├── systematic-debugging/SKILL.md # Structured debugging approach
│   ├── planning-with-files/SKILL.md  # Plan complex tasks using files
│   ├── ideation-to-plan/SKILL.md     # 🔑 Full pipeline: idea → design → plan → tasks
│   ├── project-onboarding/SKILL.md   # 🔑 Auto-init new project
│   ├── context-recovery/SKILL.md     # 🔑 Recover context when lost
│   └── hackathon-sprint/SKILL.md     # 🚀 HACKATHON: điều phối → WORKFLOW.md (Domain→Modules→HL→LL→Impl→Tasks→Execute)
│
├── rules/                            # AI behavioral rules
│   ├── behaviors.md                  # General behavioral rules
│   ├── skill-triggers.md             # When to activate which skill
│   ├── memory-flush.md               # Memory lifecycle rules
│   └── communication-protocol.md     # 🔑 Inter-agent messaging protocol
│
└── commands/                         # Slash commands
    ├── idea.md                       # /idea — start ideation pipeline
    ├── design.md                     # /design — create system design
    ├── onboard.md                    # /onboard — auto-init project
    ├── context.md                    # /context — show context map
    ├── debug.md                      # /debug — systematic debugging
    ├── deploy.md                     # /deploy — deployment pipeline
    ├── review.md                     # /review — tech lead review
    ├── sprint-end.md                 # /sprint-end — close sprint
    └── hackathon.md                  # 🚀 /hackathon — 48h hackathon launch system
```

---

## 🔍 Quick Lookup — What You Need, Where to Find It

| I want to know... | Read this file |
|-------------------|---------------|
| **Hướng dẫn sử dụng (Enter → xong hệ thống)** | `docs/onboarding/HUONG-DAN-SU-DUNG.md` |
| **Hackathon — hướng dẫn step-by-step** | `docs/onboarding/HACKATHON-GUIDE.md` |
| **Hackathon pipeline (SSOT prompts)** | `WORKFLOW.md` |
| Cheat sheet ngày thi | `HACKATHON-DAY.md` |
| **Đang ở task nào / đọc gì** | `docs/design/REPO-INDEX.md` |
| Backend map | `docs/design/BE-INDEX.md` |
| Frontend map | `docs/design/FE-INDEX.md` |
| AI map | `docs/design/AI-INDEX.md` |
| Core platform (hackathon) | `architecture.md` |
| Stack + conventions | `architecture/PROJECT.md` |
| Đề bài hackathon | `docs/PRD/hackathon-brief.md` |
| Domain Pack | `docs/PRD/hackathon-domain-pack.md` |
| Module Specs | `docs/design/hackathon-module-specs.md` |
| High-level design (+ folder FE/BE) | `docs/design/hackathon-hl-design.md` |
| Low-level design (+ file paths) | `docs/design/hackathon-ll-design.md` |
| Impl plan + milestones | `docs/design/hackathon-impl-plan.md` |
| Task sprints | `tasks/active/HAK-{BE,FE,AI}-sprint.json` |
| Current task being worked on | `memory/hot/state.json` |
| Where is the project right now | `memory/hot/context-map.md` |
| Details of a specific task | `tasks/active/[id].json` |
| Tech stack + conventions | `architecture/PROJECT.md` |
| Branch/commit naming | `architecture/GIT-WORKFLOW.md` |
| Which port a service runs on | `architecture/ENV-MAP.md` |
| How an architecture decision was made | `architecture/adr/INDEX.md` |
| Learned patterns on topic Z | `memory/warm/patterns/[topic].md` |
| Which agent handles this type of task | Agent Routing table below |
| Which skill for this workflow | Skill Triggers table below |

---

## 🤖 Agent Routing — 3 Layer Architecture

### Strategy Layer (HIGH-LEVEL DECISIONS)

| Request type | Agent | When to invoke |
|-------------|-------|---------------|
| System design, architecture vision | `cto` | New project, new major feature, technology choices |
| ADR creation & review | `cto` | Any architecture-level decision |
| Tech strategy, risk assessment | `cto` | Quarterly planning, major pivots |

### Planning Layer (BREAKDOWN & COORDINATION)

| Request type | Agent | When to invoke |
|-------------|-------|---------------|
| PRD, roadmap, sprint planning | `pm` | Feature request, sprint start, OKR review |
| Task breakdown, assignment, tracking | `pm` | Any new work item |
| Technical task decomposition | `tech-lead` | Complex tasks needing code-level planning |
| Code review, architecture guard | `tech-lead` | Before merge, PR review |
| Convention enforcement | `tech-lead` | When coding patterns are questioned |

### Execution Layer (BUILDING)

| Request type | Agent | When to invoke |
|-------------|-------|---------------|
| UI, components, pages, styling | `fe` | "button", "form", "page", "design", "CSS" |
| API, database, services, infra | `be` | "API", "endpoint", "schema", "query", "migration" |
| AI pipeline, prompts, LLM, RAG | `ai` | "AI", "LLM", "prompt", "pipeline", "embedding" |
| Testing, verification, QA | `qa` | "test", "verify", "quality", "bug report" |
| Security audit, auth, compliance | `security` | "auth", "security", "vulnerability", "audit" |

### Multi-Agent Tasks

| Scenario | Agent combination |
|----------|------------------|
| Full feature (FE + BE) | PM creates 2 parallel tasks → fe + be (after API contract defined) |
| New AI feature | CTO designs → PM plans → ai + be implement → qa verifies |
| Security-sensitive feature | security reviews → be implements → qa verifies |

---

## 🛠️ Skill Triggers

| Situation | Skill |
|-----------|-------|
| Human says "I have an idea for..." | `skills/ideation-to-plan/SKILL.md` |
| New project needs to be initialized | `skills/project-onboarding/SKILL.md` |
| Lost context, new session, confused | `skills/context-recovery/SKILL.md` |
| About to commit code | `skills/git-commit/SKILL.md` |
| Saying "done" / "complete" | `skills/verification/SKILL.md` — verify first |
| End of sprint | `skills/session-end/SKILL.md` |
| Bug with unclear root cause | `skills/systematic-debugging/SKILL.md` |
| Complex task, unclear scope | `skills/planning-with-files/SKILL.md` |
| Multi-step AI pipeline | `skills/agentic-execution/SKILL.md` |
| 🚀 **Hackathon: đề bài → code trong 48h** | `skills/hackathon-sprint/SKILL.md` |

---

## 📊 Memory TTL Policy

| Tier | Location | TTL | Pruned when |
|------|----------|-----|-------------|
| Hot | `memory/hot/` | 1 week | Sprint-end |
| Warm | `memory/warm/` | 1 quarter | Quarter-end |
| Cold | `memory/cold/` | Forever | Manual review |

**Promote rule:** Hot insight → warm/patterns when reused 2+ times in a sprint
**Demote rule:** Warm pattern unused for 2 quarters → cold archive

---

## 🔄 Project Phase Lifecycle

```
ideation → design → planning → development → testing → deployment → maintenance
    │         │         │           │            │          │           │
   CTO      CTO       PM       FE/BE/AI       QA      BE/DevOps    All
            + TL      + TL      + QA                   + Security
```

Current phase is tracked in `memory/hot/state.json → project_phase.current`
