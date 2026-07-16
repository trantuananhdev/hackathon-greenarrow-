# Skill: verification — Verify Before Claiming Done

**Trigger:** Any agent says "done", "complete", "finished" | `/done [task-id]`
**Rule:** NEVER claim done without running this skill.

---

## Protocol

```
1. Read task file → get acceptance_criteria + verify_gate
2. Run verify_gate command(s) → capture output
3. Check each acceptance criterion → demonstrably met?
4. All pass → approve done status
5. Any fail → report specific failure, DO NOT mark done
```

## Verify Gate Checklist

```
□ verify_gate command runs successfully
□ All acceptance criteria met (checked against actual output)
□ No new lint warnings
□ Tests pass
□ Build succeeds
□ No debug artifacts in code
□ Task scope not exceeded
```

## Output

```
✅ Verification PASSED — [task-id]
- Gate: [command] → PASS
- Criteria: [X/X] met
- Ready to commit

OR

❌ Verification FAILED — [task-id]
- Failed: [specific criterion/test]
- Error: [details]
- Suggested fix: [if obvious]
```
