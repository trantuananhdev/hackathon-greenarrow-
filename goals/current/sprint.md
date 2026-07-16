# Sprint [N] — Current Goals

> **"Current" = always right now.**
> At sprint end, this file is moved to `goals/archive/[YYYY-Q#]/sprint-[N].md`
> and a new file is created for the next sprint. No history in this file.

---

## 🎯 Sprint Goal (1 sentence)
> [e.g., "Build the memory layer v4 with lazy loading and TTL so AI boots under 5 seconds"]

**Sprint:** S[N] | **From:** [YYYY-MM-DD] → **To:** [YYYY-MM-DD]
**OKR Link:** `goals/current/quarter.md → OKR[X] → KR[Y]`

---

## 📋 Sprint Backlog

| ID | Task | Agent | Points | Status | Verify Gate |
|----|------|-------|--------|--------|-------------|
| S[N]-01 | [Short name] | fe | 3 | 🔵 Todo | `npm test:unit` |
| S[N]-02 | [...] | be | 5 | 🟡 In Progress | `npm test:api` |
| S[N]-03 | [...] | qa | 2 | 🟢 Done ✅ | passed |
| S[N]-04 | [...] | human | 1 | 🔴 Blocked | [reason] |

**Velocity:** [X] points done / [Y] planned
**Status legend:** 🔵 Todo · 🟡 In Progress · 🟢 Done · 🔴 Blocked · ⏸️ Waiting

---

## ✅ Definition of Done (this sprint)

- [ ] Code passes all relevant tests (unit + integration)
- [ ] Verified with actual command execution — not "should work"
- [ ] Committed with conventional commits format
- [ ] `tasks/active/[id].json` moved to `tasks/done/`
- [ ] `memory/hot/state.json` updated: `task_counts` + `next_action`
- [ ] `memory/hot/context-map.md` updated
- [ ] Architecture changes → ADR created before merge
- [ ] Documentation updated if applicable

---

## 🚧 Blockers This Sprint

```
[Task ID] | [Blocker description] | [What's needed to unblock] | [Owner]
```

---

## 🔁 Retrospective (fill at sprint-end)

**Start:** [...]
**Stop:** [...]
**Continue:** [...]
**Velocity:** [X/Y points] | New patterns: [N] | New ADRs: [N]
