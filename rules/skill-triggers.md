# Skill Triggers — When to Activate Which Skill

> Automatic trigger conditions. AI should recognize these patterns and activate the right skill.

---

| Pattern Detected | Trigger Skill |
|-----------------|---------------|
| "I have an idea...", "I want to build...", `/idea` | `skills/ideation-to-plan/SKILL.md` |
| New project, `/onboard`, "here's my codebase" | `skills/project-onboarding/SKILL.md` |
| New session, "where was I?", `/context` | `skills/context-recovery/SKILL.md` |
| "done", "finished", "complete", `/done` | `skills/verification/SKILL.md` |
| About to commit, `/commit` | `skills/git-commit/SKILL.md` |
| End of sprint, `/sprint-end` | `skills/session-end/SKILL.md` |
| Bug, error, "doesn't work", unclear cause | `skills/systematic-debugging/SKILL.md` |
| Complex task, unclear scope, many unknowns | `skills/planning-with-files/SKILL.md` |
| Multi-step pipeline, "do the whole thing" | `skills/agentic-execution/SKILL.md` |
| `/hackathon`, đề bài BTC, "hackathon 48h" | `skills/hackathon-sprint/SKILL.md` → SSOT `WORKFLOW.md` |

---

## Priority (when multiple triggers match)

1. **Safety first** — security issues override everything
2. **Verification** — always verify before commit
3. **Context** — recover context before doing work
4. **Planning** — plan before executing
5. **Execution** — do the work last
