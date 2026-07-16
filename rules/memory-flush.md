# Memory Flush Rules

> How memory moves between tiers. Enforced at sprint-end.

---

## Lifecycle

```
New insight → memory/hot/today.md
    │
    ├── Used 2+ times in sprint → PROMOTE to memory/warm/patterns/[topic].md
    │
    └── Used only once → stays in hot, pruned at sprint-end

Warm pattern → memory/warm/patterns/
    │
    ├── Used in sprint → stays warm (TTL reset)
    │
    └── Unused 2 consecutive quarters → DEMOTE to memory/cold/[YYYY-Q#]/

Cold archive → memory/cold/
    └── Manual review only, never auto-deleted
```

## Rules

1. **Hot memory resets every sprint-end** — today.md cleared, state.json updated
2. **Warm patterns have TTL of 1 quarter** — checked at quarter-end
3. **Cold is forever** — only human can delete
4. **Promote actively** — if you use an insight twice, promote it immediately
5. **context-map.md is NEVER pruned** — always current, always updated
