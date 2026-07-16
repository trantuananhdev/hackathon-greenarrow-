# /onboard — Auto-Init Project

**Usage:** `/onboard [path-to-project]`

## What Happens

```
1. Activate: skills/project-onboarding/SKILL.md
2. Scan project directory → detect tech stack
3. Generate PROJECT.md, ENV-MAP.md (filled)
4. Initialize state.json + context-map.md
5. Prompt for mission + goals
6. Suggest initial sprint
7. Report readiness
```

## Example
```
/onboard ./my-project
/onboard C:\projects\web-app
```
