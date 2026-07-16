# API Documentation — [Service Name]

**Base URL:** `[base-url]`
**Version:** [v1]
**Auth:** [JWT Bearer / API Key / None]
**Last updated:** [YYYY-MM-DD]

---

## Authentication

```
Authorization: Bearer [token]
```

[Describe how to obtain a token if applicable]

---

## Endpoints

### [Resource Name]

#### List [Resources]
```
GET /api/[resources]
```

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| limit | integer | No | 20 | Items per page |
| sort | string | No | created_at | Sort field |

**Response 200:**
```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

---

#### Create [Resource]
```
POST /api/[resources]
```

**Request Body:**
```json
{
  "field_1": "string (required)",
  "field_2": "number (optional)"
}
```

**Response 201:**
```json
{
  "data": { "id": "...", ... }
}
```

**Error Responses:**
| Code | Error | Description |
|------|-------|-------------|
| 400 | validation_error | Invalid input |
| 401 | unauthorized | Missing/invalid token |
| 409 | conflict | Resource already exists |

---

#### Get [Resource]
```
GET /api/[resources]/:id
```

**Response 200:**
```json
{
  "data": { "id": "...", ... }
}
```

---

#### Update [Resource]
```
PUT /api/[resources]/:id
```

---

#### Delete [Resource]
```
DELETE /api/[resources]/:id
```

---

## Error Format

All errors follow this format:
```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "details": {} 
}
```

## Rate Limiting
- Rate: [X requests per Y seconds]
- Header: `X-RateLimit-Remaining`

---

*Maintained by: [be agent] | Related ADR: [if any]*
