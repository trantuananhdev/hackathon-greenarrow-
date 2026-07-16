# Project Setup — How to Onboard a New Project

> This guide covers both automatic and manual project onboarding.

---

## Option A: Automatic Onboarding (Recommended)

```
/onboard [path-to-project]
```

This triggers `skills/project-onboarding/SKILL.md` which:

1. **Scans** the project directory structure
2. **Detects** tech stack (language, framework, database, etc.)
3. **Generates** `architecture/PROJECT.md` (filled with detected info)
4. **Generates** `architecture/ENV-MAP.md` (scanned services/ports)
5. **Prompts** you to fill `goals/current/mission.md`
6. **Suggests** initial sprint based on project state
7. **Reports** readiness status

---

## Option B: Manual Setup

### 1. Copy the workflow folder
```
Copy claude-code-workflow-v4/ into your project root
```

### 2. Fill required files (in this order)

#### goals/current/mission.md
- Why does this project exist? (1-2 sentences)
- Definition of success (3-5 measurable goals)

#### goals/current/quarter.md
- What are this quarter's OKRs?
- 2-3 objectives with measurable key results

#### architecture/PROJECT.md
- Project name, type, language, framework
- Folder structure
- Naming conventions
- Test strategy
- Run/build commands

#### architecture/ENV-MAP.md
- Services and their ports
- Environment variables
- Secrets management approach

### 3. Boot the system
```
Send BOOT.md to your AI assistant
```

### 4. Verify
```
/status → Should show complete system status
/context → Should show project position
```

---

## Onboarding Checklist

```
□ mission.md filled — project purpose clear
□ quarter.md filled — at least 1 OKR defined
□ PROJECT.md filled — tech stack + conventions documented
□ ENV-MAP.md filled — services + env vars mapped
□ Sprint created — goals/current/sprint.md has at least 1 task
□ Boot successful — /status shows clean report
□ First task created — tasks/active/ has at least 1 file
```

**Done. System is ready to work autonomously.**
