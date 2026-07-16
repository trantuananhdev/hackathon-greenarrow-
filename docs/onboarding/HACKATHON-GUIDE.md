# Hướng dẫn Hackathon 48h — Step by Step

> Dành cho **ai chưa từng dùng hệ thống**.  
> Bạn không cần biết code để chạy giai planning. Bạn chỉ: **dán đề bài → Enter → Review → Enter tiếp**.  
> Hệ thống chạy như một **phòng IT**: BA → CTO → Tech Lead → DEV.

**Bắt đầu từ đây (master):** [`HUONG-DAN-SU-DUNG.md`](./HUONG-DAN-SU-DUNG.md)  
**SSOT prompt:** [`WORKFLOW.md`](../../WORKFLOW.md)  
**Cheat sheet ngày thi:** [`HACKATHON-DAY.md`](../../HACKATHON-DAY.md)

---

## 1. Ý tưởng cốt lõi (đọc 1 phút)

| Trong công ty thật | Trong hệ thống này |
|--------------------|--------------------|
| Đưa đề bài cho BA | Paste vào `docs/PRD/hackathon-brief.md` |
| BA phân tích nghiệp vụ | **Enter** Prompt Phase 1–2 |
| CTO thiết kế hệ thống | **Enter** Prompt Phase 3–4 |
| Tech Lead chia việc | **Enter** Prompt Phase 5–6 |
| DEV code | **Enter** Prompt Phase 7 (mỗi người 1 chat) |
| Sếp duyệt | Bạn đọc checklist → Approve → phase sau |

AI **tự đọc / tự ghi file**. Bạn **không** copy nội dung tài liệu vào prompt — chỉ copy khối Prompt trong `WORKFLOW.md`.

```
Đề bài → BA → CTO → Tech Lead → DEV
         ↑_________________________|
              bạn chỉ Enter + Review
```

---

## 2. Chuẩn bị (một lần, trước giờ G)

### Bước 2.1 — Có đúng thư mục workflow

Repo (hoặc thư mục) phải chứa ít nhất:

- `WORKFLOW.md`
- `docs/PRD/hackathon-brief.md`
- `docs/design/REPO-INDEX.md`, `BE-INDEX.md`, `FE-INDEX.md`, `AI-INDEX.md`
- `architecture.md` (core platform) và/hoặc `architecture/PROJECT.md`

### Bước 2.2 — Tool

- Claude / Cursor / ChatGPT (có quyền đọc-ghi file trong repo thì tốt nhất — Cursor Agent / Claude Code)
- Nếu AI **không** ghi được file: sau mỗi phase, bảo AI in full markdown → bạn lưu đúng path trong bảng dưới

### Bước 2.3 — Người

| Người | Việc |
|-------|------|
| 1 Product Owner / Team Lead | Dán đề bài, Approve từng phase, assign task |
| 1–2 BE | Session Phase 7 BE |
| 1 FE | Session Phase 7 FE |
| 1 AI Eng | Session Phase 7 AI |

Planning (Phase 1–6) có thể **một người** Enter liên tục trên **một** chat.

---

## 3. Bắt đầu — chỉ cần đề bài

### Bước 3.1 — Dán đề bài

1. Mở `docs/PRD/hackathon-brief.md`
2. Xóa placeholder
3. Paste đề bài BTC vào đúng các section
4. Lưu file

### Bước 3.2 — Mở AI session chính (phòng planning)

Hai cách (chọn 1):

**Cách A — Slash (nếu AI hiểu command)**

```
/hackathon
```

AI chạy Phase 1 (vai BA). Sau mỗi phase bạn gõ:

```
/hackathon-approve
```

**Cách B — Copy prompt thủ công (luôn đúng)**

1. Mở `WORKFLOW.md`
2. Tìm `### Prompt — copy nguyên khối` của Phase đang làm
3. Copy **cả khối trong ``` **
4. Paste vào AI → **Enter**
5. Đợi AI ghi file xong + in checklist
6. Bạn review (mục 4) → Approve
7. Copy Prompt phase **kế** → Enter lại

---

## 4. Vòng lặp chuẩn (lặp 6 lần trước khi code)

```
Copy Prompt → Enter → AI ghi file → Bạn đọc checklist
     │
     ├─ Chưa ổn → gõ: /hackathon-revise [yêu cầu]
     │              hoặc paste lại prompt + “sửa theo: …”
     │
     └─ OK → Approve (/hackathon-approve hoặc nói “Approve, sang phase sau”)
              → Copy Prompt phase kế → Enter
```

### Checklist nhanh theo vai

| Phase | Vai | Bạn duyệt gì? | File phải xuất hiện |
|-------|-----|---------------|---------------------|
| 1 | BA | MVP 3–5 Must Have demo được 48h? | `docs/PRD/hackathon-domain-pack.md` |
| 2 | BA | Mọi Must Have map vào module? | `docs/design/hackathon-module-specs.md` |
| 3 | CTO | Có cây folder **FE + BE**? Index seed? | `hackathon-hl-design.md` + `*-INDEX.md` |
| 4 | CTO | Mỗi module NEW có path file? | `hackathon-ll-design.md` + INDEX cập nhật |
| 5 | Tech Lead | Critical path + H+12 core loop? | `hackathon-impl-plan.md` |
| 6 | Tech Lead | Task có `dev_prompt` + đọc INDEX? | `tasks/active/HAK-*-sprint.json` |

Kiểm tra đang ở đâu bất cứ lúc nào:

```
/hackathon-status
```

hoặc mở `docs/design/REPO-INDEX.md`.

---

## 5. Chạy lần lượt (script Enter)

Làm **đúng thứ tự** — không nhảy cóc.

### Enter 1 — BA · Domain

- Prompt: `WORKFLOW.md` → Phase 1  
- Xong → Approve

### Enter 2 — BA · Module Specs

- Prompt: Phase 2  
- Xong → Approve  
- → **Đổi vai sang CTO**

### Enter 3 — CTO · High-Level (+ folder FE/BE + seed INDEX)

- Prompt: Phase 3  
- Xong → Approve

### Enter 4 — CTO · Low-Level (+ map path vào INDEX)

- Prompt: Phase 4  
- Xong → Approve  
- → **Đổi vai sang Tech Lead**

### Enter 5 — Tech Lead · Impl Plan

- Prompt: Phase 5  
- Xong → Approve

### Enter 6 — Tech Lead · Tasks

- Prompt: Phase 6  
- Gán tên người vào `assigned_to` trong từng task (JSON)  
- Xong → `/hackathon-go`  
- → **Đổi vai sang DEV**

### Enter 7+ — DEV (song song)

Mỗi người mở **chat mới**:

| Dev | Làm gì |
|-----|--------|
| BE | Copy Prompt “session BE” Phase 7 trong `WORKFLOW.md` → Enter |
| FE | Copy Prompt “session FE” → Enter |
| AI | Copy Prompt “session AI” → Enter |

DEV **không** cần đọc lại toàn bộ design. Chỉ cần:

1. `docs/design/REPO-INDEX.md` — đang ở đâu  
2. `docs/design/BE-INDEX.md` (hoặc FE/AI) — task hiện tại, đọc gì, ghi đâu  
3. Làm theo `dev_prompt` trong `HAK-*-sprint.json`

Khi xong một task:

```
/done [task-id]
```

AI phải verify + cập nhật INDEX (task kế tiếp hiện trên Current focus).

---

## 6. Session mới / người nhảy vào giữa chừng

**Planning chưa xong:** mở `REPO-INDEX.md` xem phase → copy đúng Prompt phase đó trong `WORKFLOW.md`.

**Đang code:** 

```
1. docs/design/REPO-INDEX.md
2. docs/design/{BE|FE|AI}-INDEX.md
3. Paste Prompt Phase 7 đúng track → Enter
```

---

## 7. Bản đồ file (một trang)

```
INPUT
  docs/PRD/hackathon-brief.md          ← bạn dán đề bài

BA viết
  docs/PRD/hackathon-domain-pack.md
  docs/design/hackathon-module-specs.md

CTO viết
  docs/design/hackathon-hl-design.md    ← có folder FE/BE
  docs/design/hackathon-ll-design.md    ← có path file
  docs/design/REPO-INDEX.md            ← cập nhật sống
  docs/design/BE-INDEX.md
  docs/design/FE-INDEX.md
  docs/design/AI-INDEX.md

Tech Lead viết
  docs/design/hackathon-impl-plan.md
  tasks/active/HAK-BE-sprint.json
  tasks/active/HAK-FE-sprint.json
  tasks/active/HAK-AI-sprint.json

DEV đọc trước khi code
  REPO-INDEX → track INDEX → task JSON → ll-design (section)
```

Core / convention (AI đọc, bạn ít đụng):

- `architecture.md` — nền tảng core hackathon  
- `architecture/PROJECT.md` — stack + convention repo

---

## 8. Milestone giờ vàng

| Giờ | Phải xong |
|-----|-----------|
| H+1 | Domain (BA) approved |
| H+2 | Module Specs approved |
| H+3 | HL + LL (CTO) approved |
| H+4 | Plan + Tasks + DEV bắt đầu code |
| H+12 | **Core loop live** (tin → AI trả lời) |
| H+24 | Domain features |
| H+36 | FE↔BE integrate |
| H+44 | Demo ready |
| H+48 | Present |

Cắt scope nếu trễ: **Core loop > Domain > Admin UI > Polish**

---

## 9. Lệnh thường dùng

| Lệnh | Khi nào |
|------|---------|
| `/hackathon` | Bắt đầu / chạy phase còn thiếu |
| `/hackathon-approve` | Duyệt phase → phase sau |
| `/hackathon-revise …` | Sửa output phase hiện tại |
| `/hackathon-status` | Đang ở phase nào |
| `/hackathon-go` | Tasks đã assign → DEV |
| `/done [id]` | Task xong (có verify) |
| `/block [id] [lý do]` | Task kẹt |

Không có AI slash? Nói tiếng Việt cùng nghĩa, ví dụ: *“Approve phase này, chạy phase kế theo WORKFLOW.md”*.

---

## 10. Lỗi thường gặp

| Triệu chứng | Cách xử |
|-------------|---------|
| AI hỏi lại nội dung đề bài | Brief chưa điền / path sai — kiểm tra `hackathon-brief.md` |
| AI bịa folder | Chưa chạy Phase 3 hoặc Execute không đọc INDEX — bắt đọc `BE/FE-INDEX` |
| Không biết đang task nào | Mở `REPO-INDEX.md` + track INDEX → Current focus |
| Hai nguồn khác nhau | Chỉ tin `WORKFLOW.md` — không dùng tech-spec / system-design cũ |
| Dev session lạc | Session mới: chỉ REPO-INDEX → track INDEX → Prompt P7 |

---

## 11. Checklist “sẵn sàng thi”

```
□ Đã đọc mục 1–3 của file này
□ hackathon-brief.md đã có đề bài
□ Biết mở WORKFLOW.md và copy Prompt
□ Biết vòng Review → Approve → Enter phase sau
□ Biết DEV đọc REPO-INDEX trước
□ Phân công ai session BE / FE / AI
```

**Xong.** Chỉ việc dán đề bài và Enter.

---

*Hướng dẫn người dùng. Prompt kỹ thuật chi tiết chỉ nằm trong `WORKFLOW.md`.*
