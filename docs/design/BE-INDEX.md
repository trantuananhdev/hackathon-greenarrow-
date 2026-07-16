# BE-INDEX — Backend codebase map

> Session BE: **đọc file này trước** `HAK-BE-sprint.json`.  
> Biết repo đang có gì · đọc gì · task nào · path nào.

---

## 📍 Current focus

| Field | Value |
|-------|-------|
| Current task | `[id] — [name]` hoặc `none` |
| Status | `todo / in_progress / blocked` |
| Prompt | Dùng `dev_prompt` trong task + Phase 7 BE trong `WORKFLOW.md` |
| Read-first (task này) | `[paths — điền khi nhận task]` |
| Write-to (task này) | `[paths]` |

---

## 🌳 Folder structure (target)

> Đồng bộ với `hackathon-hl-design.md` → Folder Structure BE. Cập nhật path chi tiết ở Phase 4.

```
[backend-root]/
├── ...
```

---

## 📦 Inventory — đang có gì trong repo

| Path | Status | Mục đích | Module | Related tasks |
|------|--------|----------|--------|---------------|
| `[scan Phase 3]` | EXISTING / NEW / PLANNED | | | |

**Status legend:** `EXISTING` = đã có trong repo · `PLANNED` = thiết kế chưa code · `NEW` = vừa tạo trong sprint

---

## 🗺️ Module → Path

| Module ID | Primary paths | Read when implementing | Owner |
|-----------|---------------|------------------------|-------|
| | | | |

---

## 🔎 Read guide — tìm gì thì mở đâu

| Cần biết… | Đọc |
|-----------|-----|
| API contract / schema | `hackathon-ll-design.md` → module tương ứng |
| Cây thư mục chuẩn | `hackathon-hl-design.md` → Folder Structure BE |
| Core platform (không đụng lung tung) | `architecture.md` + `architecture/PROJECT.md` |
| Task + verify | `tasks/active/HAK-BE-sprint.json` |
| Toàn repo / phase hiện tại | `docs/design/REPO-INDEX.md` |

---

## 📋 Task map (BE)

| Task id | Name | Status | Key files | Depends |
|---------|------|--------|-----------|---------|
| | | todo | | |

---

## 🔄 Sau mỗi /done

1. Đổi status task trong bảng trên + trong JSON  
2. Đổi Inventory: PLANNED → NEW/EXISTING cho file vừa tạo  
3. Cập nhật Current focus → task tiếp theo (priority cao nhất, đủ depends_on)  
4. Sync dòng BE trên `REPO-INDEX.md`
