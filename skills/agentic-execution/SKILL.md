# Skill: agentic-execution — Multi-step AI Task Execution

**Trigger:** Task with >3 sequential steps | AI pipeline | "Do the entire flow for me"
**Goal:** Execute multi-step tasks with control — never work blind, never skip verify.

---

## Pipeline Design Template

```
## Pipeline: [Name]
Input: [describe input]
Output: [describe expected output]
Failure strategy: [stop-on-error | skip-and-continue | rollback]

Steps:
1. [Step name]
   - Do: [specific action]
   - Verify: [how to check]
   - Failure: [what if fails]
   - Output → Step 2 input: [what passes forward]
```

## Execution Protocol

After each step:
1. Verify step output
2. Log result to memory/hot/today.md
3. Decide: continue / pause / abort

PAUSE and ask human when:
- Step fails for unclear reason
- Output unexpected
- Next step is destructive
- Running > 80% timeout

## Error Handling

| Error type | Action |
|-----------|--------|
| Network timeout | Retry 3x with backoff, then pause |
| Unexpected output | STOP, log, ask human |
| Partial success | Don't rollback completed parts — log state |
| Auth error | STOP immediately, report to human |
| Data corruption risk | STOP, need human review |
