# Skill: project-onboarding — Auto-Init New Project

**Trigger:** `/onboard [project-path]` | New project needs to join the system
**Goal:** Go from "I have a codebase" to "system ready to work" in <5 minutes.

---

## When to Use

```
✅ Use when:
- Onboarding an existing codebase into this workflow system
- Setting up a new project from scratch
- Human points AI to a project directory

❌ Do NOT use for:
- Projects already onboarded (check if architecture/PROJECT.md exists)
```

---

## Onboarding Pipeline

```
/onboard [project-path]
    │
    ▼
Step 1: SCAN — Detect project structure
    │
    ▼
Step 2: DETECT — Identify tech stack
    │
    ▼
Step 3: GENERATE — Create workflow files
    │
    ▼
Step 4: PROMPT — Ask human for goals
    │
    ▼
Step 5: SUGGEST — Propose initial sprint
    │
    ▼
Step 6: REPORT — Readiness status
```

---

## Step Details

### Step 1: SCAN
```bash
# Scan project directory structure
# Look for:
ls [project-path]/

# Key files to detect:
- package.json / requirements.txt / go.mod / Cargo.toml / pom.xml / etc.
- Dockerfile / docker-compose.yml
- .env / .env.example
- README.md
- tsconfig.json / pyproject.toml / etc.
- CI config (.github/workflows, .gitlab-ci, Jenkinsfile)
```

### Step 2: DETECT
```
From scanned files, determine:

1. Primary language:
   - package.json → JavaScript/TypeScript
   - requirements.txt / pyproject.toml → Python
   - go.mod → Go
   - Cargo.toml → Rust
   - pom.xml / build.gradle → Java/Kotlin

2. Framework:
   - next.config.js → Next.js
   - vite.config.ts → Vite
   - angular.json → Angular
   - manage.py → Django
   - main.go + go.mod → Go stdlib/Gin/Echo
   - Dockerfile → Containerized

3. Database:
   - docker-compose → check for postgres/mysql/mongo/redis services
   - .env → DATABASE_URL patterns

4. Services & ports:
   - docker-compose.yml → extract all services and ports
   - .env → extract PORT variables
   - Dockerfile EXPOSE statements

5. Test framework:
   - jest.config / vitest.config / pytest.ini / go test
   
6. Linting:
   - .eslintrc / .flake8 / golangci-lint / rustfmt
```

### Step 3: GENERATE
```
Using detected information, generate:

1. architecture/PROJECT.md
   - Fill: project name, type, language, framework, database
   - Fill: folder structure (from scan)
   - Fill: run/build/test commands (from package.json scripts / Makefile / etc.)
   - Fill: naming conventions (detect from existing code patterns)

2. architecture/ENV-MAP.md
   - Fill: services and ports (from docker-compose / .env)
   - Fill: environment variables (from .env.example)

3. architecture/GIT-WORKFLOW.md
   - Pre-fill with standard workflow
   - Detect existing branch strategy if .git exists

4. memory/hot/state.json
   - Set project_phase based on project maturity:
     - No code → "ideation"
     - Has code, no tests → "development"
     - Has code + tests → "testing" or "development"
     - Has CI/CD → "deployment" capable
   - Initialize all counters to 0

5. memory/hot/context-map.md
   - Fill with detected project position
```

### Step 4: PROMPT
```
Present to human:

## 🏗️ Project Onboarded: [name]

Detected:
- Language: [X]
- Framework: [Y]
- Database: [Z]
- Services: [N] services detected

Generated:
✅ architecture/PROJECT.md (filled from scan)
✅ architecture/ENV-MAP.md (filled from scan)
✅ memory/hot/state.json (initialized)

Still needed from you:
1. goals/current/mission.md — Why does this project exist?
2. goals/current/quarter.md — What are this quarter's goals?
3. Review architecture/PROJECT.md — Are the detected conventions correct?

[Or describe your project goals and I'll fill them for you]
```

### Step 5: SUGGEST
```
Based on project state, suggest initial sprint:

If project has no tests:
  → "Sprint 1 Goal: Add test coverage to critical paths"

If project has no CI:
  → "Sprint 1 Goal: Set up CI/CD pipeline"

If project has gaps in architecture docs:
  → "Sprint 1 Goal: Document system architecture + create ADRs"

If project is feature-ready:
  → "Sprint 1 Goal: [based on human's quarter goals]"
```

### Step 6: REPORT
```
## ✅ Onboarding Complete

📁 Files generated: [N]
🔍 Tech stack detected: [language] + [framework] + [database]
🏗️ Project phase: [phase]
📋 Suggested first sprint: [suggestion]

System ready. Run /status to begin.
```

---

## Edge Cases

| Situation | Action |
|-----------|--------|
| Empty directory | Skip detection, create minimal templates, prompt for description |
| Monorepo with multiple apps | Detect each app, generate separate sections in PROJECT.md |
| No package manager detected | Ask human for tech stack, create templates manually |
| .env exists but no .env.example | WARNING: .env found without .env.example, suggest creating one |
| Already onboarded (PROJECT.md exists) | Skip, report: "Project already onboarded. Use /status instead." |
