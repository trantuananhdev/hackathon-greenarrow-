# /debug — Systematic Debugging

**Usage:** `/debug [error description]`

## What Happens
1. Activate: `skills/systematic-debugging/SKILL.md`
2. Reproduce → Hypothesize (max 3) → Test one by one → Fix → Regression test → Learn

# /deploy — Deployment Pipeline

**Usage:** `/deploy [environment]`

## What Happens
1. Run full verify gate
2. Check: all tests pass, build succeeds
3. Follow runbook: `docs/runbooks/deploy-[env].md`
4. Verify deployment health
5. Tag release if production

**Requires human approval for production.**

# /review — Tech Lead Review

**Usage:** `/review [task-id or PR]`

## What Happens
1. Tech Lead agent reads code changes
2. Checks against: PROJECT.md conventions, ADR compliance, test coverage
3. Outputs structured review with verdict

# /sprint-end — Close Sprint

**Usage:** `/sprint-end`

## What Happens
1. Activate: `skills/session-end/SKILL.md`
2. Close tasks → retrospective → memory prune → archive → prepare next sprint
