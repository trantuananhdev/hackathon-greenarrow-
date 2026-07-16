# Skill: ideation-to-plan — Full Pipeline: Idea → Design → Plan → Tasks

**Trigger:** `/idea [description]` | Human provides system description | "I want to build..."
**This is the FLAGSHIP skill of v4** — the complete autonomous pipeline.

---

## When to Use

```
✅ Use when:
- Human provides a new idea, concept, or system description
- Human provides business/technical documents for a new project
- Starting a new major feature that needs design before coding
- Human says "I want to build X" or provides requirements

❌ Do NOT use for:
- Bug fixes (→ assign directly to agent)
- Simple tasks that don't need design (→ PM creates task directly)
- Existing features needing modification (→ Tech Lead breaks down)
```

---

## Pipeline Overview

```
Human: "I want to build [description]"
    │
    ▼
Phase 1: UNDERSTAND (CTO Agent)        ← ~5 min
    │   Analyze requirements
    │   Identify components, constraints, risks
    │
    ▼
Phase 2: DESIGN (CTO Agent)            ← ~15 min
    │   Create system design document
    │   Create ADRs for key decisions
    │   Define tech stack recommendations
    │
    ▼
Phase 3: PLAN (PM Agent)               ← ~10 min
    │   Create PRD from design
    │   Break into epics → stories
    │   Estimate timeline
    │
    ▼
Phase 4: BREAKDOWN (Tech Lead)         ← ~10 min
    │   Technical task decomposition
    │   Define API contracts
    │   Assign to execution agents
    │   Create sprint backlog
    │
    ▼
Phase 5: CHECKPOINT (Human)            ← Human reviews
    │   Present: System Design + PRD + Sprint Plan
    │   Human: approve / modify / reject
    │
    ▼
Phase 6: EXECUTE (Execution Agents)    ← Sprint begins
    │   Tasks created in tasks/active/
    │   Agents begin autonomous work
    │
    ▼
[Continuous: verify → commit → track → report]
```

---

## Detailed Phase Execution

### Phase 1: UNDERSTAND

**Agent:** CTO
**Input:** Human's description/documents
**Output:** Structured requirements analysis

```
1. Read human's input carefully
2. Identify:
   - Core problem being solved
   - Target users / stakeholders
   - Key features (must-have vs nice-to-have)
   - Constraints (budget, timeline, tech, compliance)
   - Integration points with external systems
3. If ambiguous → ask human 1 clarifying question (max 1)
4. Write structured analysis to proceed with
```

### Phase 2: DESIGN

**Agent:** CTO
**Input:** Requirements analysis from Phase 1
**Output:** `architecture/system-design/[name].md` + ADR(s)

```
1. Read: goals/current/mission.md (alignment check)
2. Design system architecture:
   - Component diagram
   - Data model
   - API design
   - Technology recommendations (stack-agnostic — recommend, don't assume)
   - Security considerations
   - Scalability plan
3. Write: architecture/system-design/[name].md
4. Create ADRs for each major technology decision
5. Update: architecture/adr/INDEX.md
6. Hand off to PM
```

### Phase 3: PLAN

**Agent:** PM
**Input:** System design from Phase 2
**Output:** `docs/PRD/[name].md` + initial roadmap

```
1. Read system design
2. Create PRD:
   - Problem statement
   - User stories with acceptance criteria
   - Functional & non-functional requirements
   - Scope (in/out)
   - Timeline milestones
3. Write: docs/PRD/[name].md
4. Create roadmap:
   - Phase 1 (MVP) → Phase 2 → Phase 3
   - Map to OKRs in goals/current/quarter.md
5. Hand off to Tech Lead
```

### Phase 4: BREAKDOWN

**Agent:** Tech Lead
**Input:** PRD from Phase 3 + System Design from Phase 2
**Output:** Sprint backlog with assigned tasks

```
1. Read PRD + system design
2. Break down into technical tasks:
   - Each task ≤ 8 story points
   - Each task assigned to specific agent
   - Dependencies identified
   - API contracts defined for FE+BE parallel work
3. Create task files: tasks/active/[S#-##].json
4. Update: goals/current/sprint.md
5. Update: memory/hot/state.json
```

### Phase 5: CHECKPOINT

**Present to human:**

```
## 🎯 Project Plan Ready for Review

### System Design
- Architecture: [summary]
- Key decisions: [N] ADRs created
- Tech stack: [recommendations]

### Product Requirements
- Features: [N] user stories
- Scope: [in/out summary]
- Timeline: [estimated]

### Sprint Plan
- Sprint S1: [goal]
- Tasks: [N] tasks, [P] total points
- Agent assignments: fe([N]) · be([N]) · ai([N]) · qa([N])

### What I Need From You
1. ✅ Approve to start execution?
2. ❓ Any modifications to design/plan?
3. ⚠️ Any constraints I missed?
```

### Phase 6: EXECUTE

After human approval:
```
1. Update state.json → project_phase: "development"
2. Update context-map.md → project position
3. Execution agents begin picking up tasks
4. PM tracks progress and reports
```

---

## Handling Different Input Types

### When human provides just an idea (1-2 sentences)
→ Start from Phase 1, CTO asks 1 clarifying question if needed

### When human provides business requirements document
→ Skip Phase 1 analysis, go straight to Phase 2 design
→ PM extracts user stories from the document in Phase 3

### When human provides technical specification
→ CTO validates and creates formal system design in Phase 2
→ Less analysis needed, faster pipeline

### When human provides both business + technical docs
→ CTO cross-references both, identifies gaps
→ Creates system design that satisfies both
→ Fastest path to execution

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Requirements too vague after 1 clarification | Present what's understood, list unknowns, ask human |
| Contradictory requirements | List conflicts, ask human to prioritize |
| Scope too large for 1 sprint | Break into phases, present Phase 1 MVP |
| Technology constraint makes design impossible | CTO proposes alternatives, human decides |
| Human rejects plan at checkpoint | Collect feedback, iterate from relevant phase |

---

## Output Artifacts

After this skill completes, these files should exist:
```
✅ architecture/system-design/[name].md    ← System design
✅ architecture/adr/ADR-[NNN]-[slug].md    ← Key decisions (1+)
✅ docs/PRD/[name].md                      ← Product requirements
✅ goals/current/sprint.md                 ← Updated with sprint plan
✅ tasks/active/S[N]-[##].json             ← Individual tasks (multiple)
✅ memory/hot/state.json                   ← Updated state
✅ memory/hot/context-map.md               ← Updated position
```
