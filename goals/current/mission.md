# Mission — North Star

> This file defines "why we exist". Changes <1x per year.
> Every technical decision must trace back to this.
> If a task doesn't serve this mission → question it before executing.

---

## 🌟 Mission Statement
> [1-2 sentences: What are we building, for whom, and why]

*Example: "Build an autonomous AI agent system that replaces FE/BE/AI dev teams — runs reliably, has organized memory, maintains technical discipline, and requires minimal human supervision."*

---

## 🏆 Definition of Success (12-18 months)

- [ ] System runs continuously for 30 days without manual restart
- [ ] Task completion rate >90% correct without rework
- [ ] Zero hallucinations in production code output
- [ ] AI self-detects patterns and self-improves without explicit instruction
- [ ] New project onboarding in <30 minutes (only fill PROJECT.md + goals)

---

## 🧭 Design Principles (immutable)

1. **Lazy > Eager** — Load when needed, never preemptively
2. **Index > Read** — Consult index first, read file second
3. **State machine > History** — "Now" is clearer than "flat history"
4. **File movement > Status field** — Move files between folders, don't update status strings
5. **Verify > Claim** — Never declare done without proof
6. **Single Source of Truth** — Each piece of information lives in exactly one place
7. **Every session leaves assets** — Each session produces patterns/ADR/skills for future sessions
8. **TTL on everything** — Memory, patterns, decisions — everything has an expiration date
9. **Stack agnostic** — System works with any technology, any language, any framework

---

## 🚫 Never

- Load everything into context at boot
- Store history and current state in the same file
- Claim "done" without a passing verify gate
- Create files outside the structure defined in INDEX.md
- Modify accepted ADRs — only supersede with new ones
- Commit untested code
- Assume the tech stack — always read PROJECT.md

---

*Created: [date] | Owner: [name] | Last modified: [date]*
