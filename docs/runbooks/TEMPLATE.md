# Runbook — [Procedure Name]

**Type:** [Deploy / Rollback / Incident / Maintenance / Migration]
**Severity:** [P0 Critical / P1 High / P2 Medium / P3 Low]
**Last tested:** [YYYY-MM-DD]
**Owner:** [name/agent]

---

## When to Use
> [Describe the situation that triggers this runbook]

## Prerequisites
- [ ] [Access/permission needed]
- [ ] [Tool installed]
- [ ] [Service running]

## Steps

### 1. [Step Name]
```bash
[Exact command to run]
```
**Expected output:** [What you should see]
**If fails:** [What to do]

### 2. [Step Name]
```bash
[Exact command to run]
```
**Expected output:** [...]
**If fails:** [...]

### 3. Verify
```bash
[Verification command]
```
**Success criteria:** [What confirms everything worked]

## Rollback Plan
```bash
[Commands to undo if something goes wrong]
```

## Post-Procedure
- [ ] Update `memory/hot/today.md` with results
- [ ] Notify [who] about completion
- [ ] Update monitoring/alerts if needed

---

*Last executed: [date] | By: [name] | Result: [success/failure]*
