# PROJECT.md — Project Architecture

> AI READS THIS when starting work. This is the "project map" to avoid getting lost.
> Do not guess conventions — look them up here first.
> **This template is STACK-AGNOSTIC. Fill in your project's actual stack.**

---

## 📋 Project Overview

| Field | Value |
|-------|-------|
| Project Name | Green Arrow — Điện Biên Weather Alert |
| Type | Data pipeline / CLI / notebook |
| Primary Language | Python 3.10 |
| Framework | pandas + PyArrow |
| Database | Parquet |
| Cache | [...] |
| Message Queue | [...] |
| Hosting | [...] |
| CI/CD | [...] |
| Status | Development |

---

## 🗂️ Folder Structure

```
project-root/
├── pipeline/
│   ├── build/               # build reference/master datasets
│   ├── download/            # external-source adapters
│   ├── transform/           # alerts and derived signals
│   ├── verify/              # artifact verification gates
│   └── shared/              # contracts and parsers
├── tests/pipeline/          # mirrors pipeline modules
├── data/
│   ├── reference/
│   ├── features/
│   ├── weather/
│   ├── hydrology/
│   └── events/
├── notebooks/
├── docs/
└── architecture/
```

**Key rules:**
- Each module is a separate folder
- Pipeline tests mirror the production module hierarchy under `tests/pipeline/`
- Shared code → `shared/` or `common/`, never copy-paste between modules
- Do not create files outside this structure without an ADR

---

## ⚙️ Tech Stack & Conventions

### Naming Conventions
```
[Fill in your project's conventions. Examples:]

Files:        [kebab-case.ext]        (user-service.py)
Classes:      [PascalCase]            (UserService)
Functions:    [camelCase or snake_case](get_user_by_id)
Constants:    [SCREAMING_SNAKE_CASE]  (MAX_RETRY_COUNT)
Types:        [PascalCase]            (UserProfile)
DB tables:    [snake_case]            (user_profiles)
API endpoints:[/kebab-case]           (/user-profiles)
```

### Code Patterns
```
[Fill in your project's patterns. Examples:]

# Service pattern:
# 1. Interface/Protocol first
# 2. Implementation
# 3. Unit test
# 4. No business logic in controllers/handlers

# Error handling:
# [describe pattern — Result<T,E>, exceptions, error codes, etc.]

# Async patterns:
# [describe — async/await, promises, goroutines, etc.]
```

### Import/Include Order
```
[Fill in your project's import order. Example:]

# 1. Standard library / built-ins
# 2. External packages
# 3. Internal modules (use aliases if applicable)
# 4. Relative imports
# 5. Type imports last
```

---

## 🧪 Testing Strategy

| Layer | Tool | Coverage Target | When to run |
|-------|------|----------------|-------------|
| Unit | [...] | > 80% | Pre-commit |
| Integration | [...] | Key paths | Pre-merge |
| E2E | [...] | Critical flows | Pre-deploy |

**Gate mandatory:** Do not merge if unit tests fail. Do not deploy if integration tests fail.

---

## 🚀 Run & Build Commands

```bash
# Development
[start dev command]

# Test
[test command]
[test with coverage command]

# Build
[build command]

# Lint & format
[lint command]
[format command]

# Database migration (if applicable)
[migrate up command]
[migrate down command]
```

---

## 🔌 Environment & Services

See details: `architecture/ENV-MAP.md`

| Service | Port (local) | Purpose |
|---------|-------------|---------|
| [...] | [...] | [...] |

---

## 📝 Rules When AI Writes Code

1. **Read related files before modifying** — do not assume
2. **Follow naming conventions** — look up the table above, do not improvise
3. **Write tests at the same time as code** — never leave TODO tests
4. **Do not modify public interfaces** — create a new version instead
5. **All breaking changes** → need ADR before implementation
6. **After writing code** → run lint + test → if passes → commit
7. **Stack-specific**: [Add any project-specific rules here]

---

## 🏗️ AI-Specific Instructions

> This section tells AI how to approach THIS particular project.

```
[Fill in project-specific AI instructions. Examples:]

- When writing API endpoints, always include input validation middleware
- Use [specific ORM/query builder] for database access
- Error responses follow [specific format]
- All dates use ISO 8601 format
- Multi-tenant: always include tenant_id in queries
```

---

*Updated: [date] | Related ADRs: see `architecture/adr/`*
