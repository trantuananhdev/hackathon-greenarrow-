# Skill: systematic-debugging — Structured Debugging

**Trigger:** Bug with unclear root cause | "It doesn't work" | Error that isn't obvious

---

## Protocol

```
Step 1: REPRODUCE
- Get exact steps to reproduce
- Get exact error message/behavior
- Confirm: reproducible or intermittent?

Step 2: HYPOTHESIZE (max 3 hypotheses)
- H1: [most likely cause] → test by [action]
- H2: [second possibility] → test by [action]
- H3: [least likely] → test by [action]

Step 3: TEST (one hypothesis at a time)
- Test H1 → confirmed/rejected
- If rejected → test H2
- Document each test result

Step 4: FIX
- Implement fix for confirmed cause
- Write regression test
- Verify fix doesn't break other things

Step 5: LEARN
- /learn [what caused this, how to prevent]
- Update patterns if applicable
```

## Anti-patterns

```
❌ Changing random things hoping it fixes
❌ Skipping reproduction step
❌ Testing all hypotheses simultaneously
❌ Fixing without adding regression test
❌ Not documenting the root cause
```
