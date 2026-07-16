# System Design — [Project/Feature Name]

**Status:** 🔄 Draft / ✅ Approved / 🔁 Superseded
**Author:** [CTO Agent / name]
**Date:** [YYYY-MM-DD]
**Related PRD:** `docs/PRD/[feature].md`
**Related ADRs:** ADR-[NNN]

---

## 1. Overview

### Problem Statement
> [What problem are we solving? 2-3 sentences max]

### Goals
- [Goal 1]
- [Goal 2]
- [Goal 3]

### Non-Goals (explicitly out of scope)
- [Non-goal 1]
- [Non-goal 2]

---

## 2. Architecture

### High-Level Diagram
```
[ASCII diagram or description of system components and their interactions]

[Component A] ──→ [Component B] ──→ [Component C]
      │                                    │
      └────────── [Component D] ←──────────┘
```

### Component Breakdown

| Component | Responsibility | Technology | Owner Agent |
|-----------|---------------|------------|-------------|
| [Name] | [What it does] | [Tech] | [fe/be/ai] |
| [Name] | [...] | [...] | [...] |

### Data Flow
```
1. User → [entry point] → [processing] → [storage] → [response]
2. [Describe primary data flows]
```

---

## 3. Data Model

### Entity Relationship
```
[User] 1──* [Order] *──1 [Product]
              │
              └──* [OrderItem]
```

### Key Schemas
```
[Use your project's data definition format]

Table/Collection: [name]
- field_1: type (constraints)
- field_2: type (constraints)
- field_3: type (constraints)
```

---

## 4. API Design

### Endpoints
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /api/[resource] | List all | Token |
| POST | /api/[resource] | Create | Token |
| GET | /api/[resource]/:id | Get one | Token |
| PUT | /api/[resource]/:id | Update | Token |
| DELETE | /api/[resource]/:id | Delete | Admin |

### Request/Response Contracts
```
POST /api/[resource]
Request:  { field: type, ... }
Response: { data: {...}, meta: {...} }
Error:    { error: "code", message: "..." }
```

---

## 5. Security Considerations
- [ ] Authentication: [method]
- [ ] Authorization: [method]
- [ ] Data encryption: [at rest / in transit]
- [ ] Input validation: [approach]
- [ ] Rate limiting: [if applicable]

---

## 6. Scalability & Performance
- Expected load: [X requests/sec, Y concurrent users]
- Bottlenecks: [identified areas]
- Caching strategy: [what, where, TTL]
- Scaling approach: [horizontal/vertical, auto-scaling]

---

## 7. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | [H/M/L] | [H/M/L] | [Plan] |
| [Risk 2] | [...] | [...] | [...] |

---

## 8. Implementation Plan

| Phase | Tasks | Agent | Estimated |
|-------|-------|-------|-----------|
| Phase 1 | [Core setup] | be | [X days] |
| Phase 2 | [Feature build] | fe + be | [X days] |
| Phase 3 | [Testing] | qa | [X days] |
| Phase 4 | [Deploy] | be | [X days] |

---

## 9. Open Questions

- [ ] [Question that needs human/team input before proceeding]
- [ ] [Another open question]

---

*Approved by: [name] | Approved on: [date]*
