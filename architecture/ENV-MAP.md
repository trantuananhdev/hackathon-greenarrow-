# ENV-MAP.md — Environment & Services Map

> AI consults this file when needing to know which service runs where, which port, which env var.
> Never hardcode — always use env var names from this table.

---

## 🌍 Environments

| Environment | Branch | URL/Host | Purpose |
|-------------|--------|----------|---------|
| Local | any | localhost | Development |
| Staging | develop | [staging-url] | Integration test |
| Production | main | [prod-url] | Live |

---

## 🔌 Services Map

| Service | Local Port | Staging | Production | Env Var |
|---------|-----------|---------|------------|---------|
| [API Server] | [3000] | [...] | [...] | `API_PORT` |
| [Database] | [5432] | [...] | [...] | `DATABASE_URL` |
| [Cache] | [6379] | [...] | [...] | `REDIS_URL` |
| [Other service] | [...] | [...] | [...] | [...] |

---

## 🔑 Environment Variables Reference

```bash
# .env.example (commit this file, NEVER commit .env)

# === APP ===
NODE_ENV=development
API_PORT=3000
LOG_LEVEL=debug

# === DATABASE ===
DATABASE_URL=[connection-string]

# === CACHE ===
REDIS_URL=redis://localhost:6379

# === AUTHENTICATION ===
JWT_SECRET=your-secret-here
JWT_EXPIRES_IN=7d

# === EXTERNAL SERVICES ===
# [Add your service keys here]

# === FEATURE FLAGS ===
FEATURE_AUTO_COMMIT=true
```

---

## 🔐 Secrets Management

| Secret | Production Storage | Who Has Access |
|--------|-------------------|---------------|
| DB password | [Vault/SSM/...] | DevOps only |
| API keys | [Vault/SSM/...] | Backend team |
| JWT secret | [Vault/SSM/...] | DevOps only |

**Rules:**
- Never commit secrets to git
- Never log secrets (even partially)
- Rotate keys when: team member leaves, suspected leak
- AI must never hardcode secret values into code

---

## 🚀 Startup Dependencies

```
Boot order:
1. [Database] (required before all)
2. [Cache] (required before API server)
3. [API Server]
4. [Other services]

Health check:
- /health → 200 OK means ready
- Timeout: 30s before considering failed
```

---

*Updated: [date] | Updated by: [name/agent]*
