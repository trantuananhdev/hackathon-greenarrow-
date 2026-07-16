# 🚀 HACKATHON DAY — Cheat Sheet

> In / giữ mở.  
> **Người mới:** đọc `docs/onboarding/HUONG-DAN-SU-DUNG.md` trước.  
> **Prompt:** `WORKFLOW.md` (SSOT).

---

## Phòng IT (Enter liên tục)

```
Đề bài → BA (P1–P2) → CTO (P3–P4) → Tech Lead (P5–P6) → DEV (P7)
              Review/Approve giữa mỗi phase
```

---

## 0 — Trước giờ G

```
□ Đọc HACKATHON-GUIDE.md (mục 1–3)
□ Điền docs/PRD/hackathon-brief.md
□ architecture.md + PROJECT.md sẵn
□ Local/Docker chạy được
□ Session: 1 planning + BE + FE + AI
```

---

## Pipeline

| # | Vai | Phase | Output |
|---|-----|-------|--------|
| 1 | BA | Domain | `hackathon-domain-pack.md` |
| 2 | BA | Module Specs | `hackathon-module-specs.md` |
| 3 | CTO | HL + folder FE/BE + INDEX | `hl-design` + `*-INDEX` |
| 4 | CTO | LL + path map | `ll-design` + INDEX |
| 5 | TL | Impl Plan | `impl-plan` |
| 6 | TL | Tasks | `HAK-*.json` |
| 7 | DEV | Execute | INDEX → code → `/done` → **auto-next** |

**Session mới / đang code:** mở `docs/design/REPO-INDEX.md` trước.

---

## Roles

| Role | Đọc trước |
|------|-----------|
| PO / TL | `REPO-INDEX.md` + `HACKATHON-GUIDE.md` |
| DEV BE | `BE-INDEX.md` → `HAK-BE-sprint.json` |
| DEV FE | `FE-INDEX.md` → `HAK-FE-sprint.json` |
| DEV AI | `AI-INDEX.md` → `HAK-AI-sprint.json` |

---

## Milestone

| Giờ | Gate |
|-----|------|
| H+4 | Tasks assigned, DEV code |
| H+12 | **Core loop live** |
| H+24 | Domain features |
| H+36 | Integration |
| H+44 | Demo ready |
| H+48 | Present |

Cắt scope: Core loop > Domain > Admin UI > Polish

---

## Lệnh

```
/hackathon | /hackathon-approve | /hackathon-revise […]
/hackathon-status | /hackathon-go
/done [task-id] | /block [task-id] [lý do]
```
