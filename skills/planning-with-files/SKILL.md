# Skill: planning-with-files — Plan Complex Tasks Using Files

**Trigger:** Complex task with unclear scope | Task > 8 story points | Multiple unknowns

---

## When to Use

```
✅ Task has multiple unknowns
✅ Task touches multiple modules/agents
✅ Task scope is unclear
✅ Human says "figure out how to do X"

❌ Simple, well-defined tasks
❌ Bug fixes with obvious cause
```

## Protocol

```
Step 1: SCOPE
- What exactly needs to be done?
- What's in scope? What's explicitly OUT?
- What information is missing?

Step 2: RESEARCH
- Read related files (architecture, patterns, existing code)
- Identify dependencies and constraints
- List unknowns

Step 3: PLAN (write to task file)
- Break into numbered steps
- Estimate each step
- Identify: which agent does what
- Define: verify criteria for each step

Step 4: REVIEW
- Present plan to human/Tech Lead
- Get approval before executing
- Adjust based on feedback

Step 5: EXECUTE
- Follow plan step by step
- Update progress in task file
- Report deviations from plan
```

## Plan Template

```markdown
## Plan: [Task Name]

### Scope
- In: [...]
- Out: [...]

### Steps
1. [ ] [Step] — [agent] — [est. time] — verify: [how]
2. [ ] [Step] — [agent] — [est. time] — verify: [how]

### Dependencies
- [Step 2 needs Step 1 output]

### Risks
- [Risk 1] → mitigation: [plan]

### Total Estimate: [X points / Y hours]
```
