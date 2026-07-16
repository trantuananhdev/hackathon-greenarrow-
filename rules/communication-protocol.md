# Communication Protocol — Inter-Agent Messaging

> Agents do NOT talk to each other directly.
> All communication happens through files.
> Agent A writes → Agent B reads → Agent B replies in the same file.

---

## Core Principle

**File System = Message Bus.** There is no other communication channel.

---

## Protocol: Agent-to-Agent Request

### 1. Write request in task file

Under `## Agent Requests` section:

```json
{
  "agent_requests": [
    {
      "id": "REQ-001",
      "from": "fe",
      "to": "be",
      "request": "Need API contract for POST /api/users",
      "priority": "high",
      "status": "waiting",
      "created": "2026-01-15T10:00:00Z",
      "response": null,
      "responded_at": null
    }
  ]
}
```

### 2. Receiving agent reads and responds

```json
{
  "id": "REQ-001",
  "status": "responded",
  "response": "API contract: POST /api/users { name: string, email: string } → 201 { data: { id, name, email } }",
  "responded_at": "2026-01-15T10:30:00Z"
}
```

### 3. Requesting agent marks resolved

```json
{
  "id": "REQ-001",
  "status": "resolved"
}
```

---

## Escalation Protocol

```
Agent → Agent:       Write in task file (normal flow)
Agent → PM:          Update task status to blocked + reason
Agent → Tech Lead:   Write in task file + tag "needs-review"
Agent → CTO:         PM escalates on agent's behalf
Agent → Human:       PM reports blocker that needs human action
```

---

## Status Values

| Status | Meaning |
|--------|---------|
| `waiting` | Request sent, waiting for response |
| `responded` | Response provided, waiting for requester to read |
| `resolved` | Request handled, conversation closed |
| `escalated` | Couldn't be resolved at this level, escalated up |

---

## Rules

1. **One question at a time** — don't overload with multiple requests
2. **Be specific** — "Need API contract for X" not "Need help"
3. **Include context** — reference task-id and what you're trying to do
4. **Respond promptly** — don't leave `waiting` requests open
5. **Never modify another agent's work** — only add your response
6. **Escalate don't stall** — if you can't respond, escalate to PM
