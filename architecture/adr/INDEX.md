# ADR Index — Architecture Decision Records

> Every important architecture decision must have an ADR.
> Accepted ADRs are IMMUTABLE — create a new ADR to supersede.

---

## ADR List

| ID | Title | Status | Date |
|----|-------|--------|------|
| ADR-001 | [Example: Choose framework X over Y] | ✅ Accepted | [...] |
| ADR-002 | [Example: Memory SSOT strategy] | ✅ Accepted | [...] |
| ADR-003 | Parquet cho dữ liệu thời tiết lịch sử | ✅ Accepted | 2026-07-17 |
| ADR-004 | Phạm vi 5 năm và phân vùng quý cho dữ liệu thời tiết | ✅ Accepted | 2026-07-17 |

**Status legend:**
- 🔄 Proposed — Under discussion
- ✅ Accepted — Applied
- ❌ Rejected — Rejected (with reason)
- 🔁 Superseded — Replaced by another ADR
- 🔵 Deprecated — No longer applicable

---

## When to Create an ADR

✅ Need ADR when:
- Choosing an important library/framework
- Changing database schema
- Changing API contract (breaking)
- Changing folder/module organization
- Security/authentication decisions
- Changing how agents/skills fundamentally work
- Technology stack decisions

❌ Don't need ADR:
- Regular bug fixes
- Adding new non-breaking endpoints
- Patch version dependency updates
- Internal module refactoring (no interface changes)
