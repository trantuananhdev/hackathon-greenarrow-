# REPO-INDEX — Bản đồ repo (Hackathon)

> **Đọc file này trước** khi làm bất kỳ task nào / khi session mới nhảy vào.  
> AI cập nhật sau mỗi phase design và sau mỗi `/done`.

---

## 📍 Đang đứng đâu

| Field | Value |
|-------|-------|
| Pipeline phase | `[0–7 / execute]` |
| Track focus | `[BE / FE / AI / TL]` |
| Current task id | `[vd: BE-01]` — sync từ HAK-*-sprint.json |
| Current task name | `[…]` |
| Prompt dùng tiếp | `WORKFLOW.md` → Phase 7 session `[BE\|FE\|AI]` |
| Blockers | `[none / …]` |

---

## 🧭 Đọc gì để làm việc (thứ tự)

| Mục đích | File |
|----------|------|
| Đề bài / MVP | `docs/PRD/hackathon-domain-pack.md` |
| Module biên giới | `docs/design/hackathon-module-specs.md` |
| Kiến trúc tổng + **cây thư mục FE/BE** | `docs/design/hackathon-hl-design.md` |
| Chi tiết implement + path file | `docs/design/hackathon-ll-design.md` |
| Thứ tự / milestone | `docs/design/hackathon-impl-plan.md` |
| **Index Backend** | `docs/design/BE-INDEX.md` |
| **Index Frontend** | `docs/design/FE-INDEX.md` |
| **Index AI** | `docs/design/AI-INDEX.md` |
| Core platform | `architecture.md` (nếu có) + `architecture/PROJECT.md` |
| Task list | `tasks/active/HAK-{BE,FE,AI}-sprint.json` |

---

## 🗂️ Folder structure (tóm tắt — chi tiết trong HL design)

```
[Điền sau Phase 3 — cây FE + BE target]
```

---

## ✅ Cách hoàn thiện dự án (Execute)

1. Mở track INDEX (`BE-INDEX` / `FE-INDEX` / `AI-INDEX`) → xem **Current task** + **Read-first**
2. Mở `HAK-*-sprint.json` → lấy `dev_prompt` của task đó
3. Paste Dev Session prompt (`WORKFLOW.md` Phase 7) nếu session mới
4. Implement đúng path trong INDEX / LL design
5. Verify → `/done [id]` → **cập nhật** track INDEX (file status + next task)

---

## 🔗 Task board (sync nhanh)

| Track | Next todo | In progress | Done count |
|-------|-----------|-------------|------------|
| BE | | | 0 |
| FE | | | 0 |
| AI | | | 0 |

---

*Sinh/ cập nhật bởi Phase 3–7 trong WORKFLOW.md. Không sửa tay lung tung — để AI cập nhật theo phase.*
