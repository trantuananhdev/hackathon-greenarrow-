# Hướng dẫn step-by-step — Bạn làm gì · Kết quả gì · Human in the loop

> **Bạn = Product Owner / Team Lead.** AI = phòng IT (BA → CTO → Tech Lead → DEV).  
> AI **không** tự Approve, **không** tự deploy, **không** tự cắt scope Must Have.  
> Mỗi cổng dưới đây bắt buộc có người duyệt.

**Prompt kỹ thuật (copy nguyên khối):** [`WORKFLOW.md`](../../WORKFLOW.md)  
**Cheat sheet ngày thi:** [`HACKATHON-DAY.md`](../../HACKATHON-DAY.md)

---

## Nguyên tắc Human-in-the-loop (HITL)

```
AI đề xuất / viết file
        ↓
HUMAN đọc checklist + file output
        ↓
    ┌───┴───┐
 Revise   Approve
    │         │
    ▼         ▼
 AI sửa    Mới được sang bước sau
```

| AI được làm tự động | **Bạn** phải làm (HITL) |
|---------------------|-------------------------|
| Đọc file, viết design/code theo prompt | Điền đề bài, chốt MVP |
| In checklist review | **Approve / Revise** mỗi phase 1–6 |
| Đề xuất task & path | Assign người, cắt scope nếu trễ |
| Chạy / đề xuất verify | Xác nhận verify pass/fail trước `/done` |
| Auto-next task sau khi bạn cho phép | Gõ `tiếp` hoặc `dừng` / `pause` |
| Cập nhật INDEX sau done | Quyết định khi blocked / cần đổi kiến trúc |

**Cấm:** gõ Approve mà chưa mở file output.  
**Cấm:** để AI tự nhảy Phase 1→6 không dừng.

---

## Tổng quan pipeline (8 bước chính)

| Bước | Ai làm việc chính | Bạn làm (HITL) | Kết quả đạt được |
|------|-------------------|----------------|------------------|
| 0 | Bạn | Chuẩn bị + điền đề bài | Input sẵn sàng |
| 1 | AI = BA | Review → Approve/Revise | Domain Pack (MVP chốt) |
| 2 | AI = BA | Review → Approve/Revise | Module Specs |
| 3 | AI = CTO | Review → Approve/Revise | HL Design + INDEX seed |
| 4 | AI = CTO | Review → Approve/Revise | LL Design + path map |
| 5 | AI = Tech Lead | Review → Approve/Revise | Impl Plan + milestone |
| 6 | AI = Tech Lead | Review → **Assign** → Approve | Task JSON 3 track |
| 7 | AI = DEV | Verify + `/done` / `tiếp` / `dừng` | Code xong từng task → demo |

Chi tiết từng bước ở dưới.

---

# BƯỚC 0 — Chuẩn bị (chỉ bạn)

### Bạn làm gì

1. Copy folder workflow này vào **root repo sản phẩm** (nơi sẽ có code FE/BE/AI).
2. Mở `architecture/PROJECT.md` → điền stack thật, lệnh `dev` / `test` / `lint`.
3. Mở `docs/PRD/hackathon-brief.md`:
   - Xóa `[PLACEHOLDER]`
   - Paste đề bài BTC (Section 1)
   - Điền tiêu chí chấm, ràng buộc tech, góc nhìn team (nếu có)
4. Phân công người: 1 PO (bạn) · BE · FE · AI Eng (có thể 1 người làm nhiều session).
5. Mở **1 chat planning** (Cursor Agent / Claude Code — có quyền ghi file).

### Kết quả đạt được

```
□ hackathon-brief.md có đề bài thật (không còn placeholder)
□ PROJECT.md có lệnh chạy/test thật
□ Team biết ai session nào
□ Chat planning sẵn sàng
```

### HITL checkpoint

- Chỉ bạn quyết định: đề bài nào là nguồn đúng, stack nào được phép dùng.
- **Chưa** chạy AI phase 1 nếu brief còn trống.

---

# BƯỚC 1 — Domain Pack · Vai AI: BA

### Bạn làm gì

1. Mở `WORKFLOW.md` → **PHASE 1** → copy khối `### Prompt — copy nguyên khối`.
2. Paste vào chat planning → Enter.
3. Đợi AI ghi file xong và in checklist.
4. **Mở file** `docs/PRD/hackathon-domain-pack.md` — đọc thật.
5. Quyết định:
   - Chưa ổn → `/hackathon-revise [yêu cầu cụ thể]` → đọc lại → lặp
   - Ổn → gõ `/hackathon-approve` (hoặc: `Approve Domain Pack, sang Phase 2`)

### Kết quả đạt được

| Có file | Nội dung bạn phải thấy |
|---------|------------------------|
| `docs/PRD/hackathon-domain-pack.md` | Mục tiêu demo 1 câu · 3–5 Must Have · User stories · Business rules · Domain tools · Seed data |

### HITL — bạn duyệt gì?

```
□ Must Have có demo được trong 48h không? (cắt nếu quá tham)
□ Stories / rules đủ để team hiểu bài toán không?
□ Tool / seed data có khớp đề bài BTC không?
→ Chỉ Approve khi bạn đồng ý MVP. Đây là cổng quan trọng nhất.
```

---

# BƯỚC 2 — Module Specs · Vai AI: BA

### Bạn làm gì

1. Copy Prompt **PHASE 2** từ `WORKFLOW.md` → Paste → Enter  
   *(hoặc sau Approve bước 1, AI tự chạy Phase 2 nếu dùng `/hackathon-approve`)*
2. Mở `docs/design/hackathon-module-specs.md`.
3. Revise hoặc Approve.

### Kết quả đạt được

| Có file | Nội dung bạn phải thấy |
|---------|------------------------|
| `hackathon-module-specs.md` | Bảng module (EXISTING/NEW) · Spec từng module NEW · Gap vs core |

### HITL — bạn duyệt gì?

```
□ Mỗi Must Have map vào ≥ 1 module?
□ Hai module có chồng trách nhiệm không?
□ Module NEW có quá nhiều so với 48h không? → bắt AI cắt
```

---

# BƯỚC 3 — High-Level Design · Vai AI: CTO

### Bạn làm gì

1. Copy Prompt **PHASE 3** → Enter (AI sẽ scan repo + viết nhiều file).
2. Đọc lần lượt:
   - `docs/design/hackathon-hl-design.md`
   - `docs/design/REPO-INDEX.md`
   - `docs/design/BE-INDEX.md` / `FE-INDEX.md` / `AI-INDEX.md` (mới seed)
3. Revise hoặc Approve.

### Kết quả đạt được

| Có / cập nhật | Nội dung |
|---------------|----------|
| `hackathon-hl-design.md` | Component diagram · data flow · contracts · **cây folder FE + BE** |
| `REPO-INDEX.md` | Phase = 3 · bảng “đọc gì” |
| `BE/FE/AI-INDEX.md` | Folder target + inventory EXISTING từ scan |

### HITL — bạn duyệt gì?

```
□ Cây thư mục FE/BE có khớp repo thật không? (không bịa folder)
□ Track BE / FE / AI tách được để làm song song không?
□ Risk / NFR có điểm nào team không chấp nhận không?
→ Kiến trúc sai ở đây = code sai hàng loạt ở bước 7.
```

---

# BƯỚC 4 — Low-Level Design · Vai AI: CTO

### Bạn làm gì

1. Copy Prompt **PHASE 4** → Enter.
2. Đọc `docs/design/hackathon-ll-design.md` + kiểm tra INDEX đã có **Module → Path**.
3. Revise hoặc Approve.

### Kết quả đạt được

| Có / cập nhật | Nội dung |
|---------------|----------|
| `hackathon-ll-design.md` | Mỗi module NEW: schema I/O · logic · API/DB · **bảng Files CREATE/EDIT** |
| `BE/FE/AI-INDEX.md` | Module→Path đủ · Inventory PLANNED |
| `REPO-INDEX.md` | Phase = 4 |

### HITL — bạn duyệt gì?

```
□ Mỗi module NEW có path file cụ thể không?
□ Path nằm đúng cây folder bước 3 không?
□ Schema / API có đủ để DEV code không cần hỏi lại bạn không?
```

---

# BƯỚC 5 — Implementation Plan · Vai AI: Tech Lead

### Bạn làm gì

1. Copy Prompt **PHASE 5** → Enter.
2. Đọc `docs/design/hackathon-impl-plan.md` cùng team (nếu có).
3. Revise hoặc Approve.

### Kết quả đạt được

| Có file | Nội dung |
|---------|----------|
| `hackathon-impl-plan.md` | Dependency · parallel tracks · milestone H+12… · timebox · risk |

### HITL — bạn duyệt gì?

```
□ Critical path có gate H+12 = core loop (tin vào → AI trả) không?
□ Track song song có đụng cùng 1 file không?
□ Timebox có thực tế với số người không? → cắt scope sớm nếu không
```

---

# BƯỚC 6 — Tasks · Vai AI: Tech Lead · Bạn: Assign

### Bạn làm gì

1. Copy Prompt **PHASE 6** → Enter.
2. Mở 3 file:
   - `tasks/active/HAK-BE-sprint.json`
   - `tasks/active/HAK-FE-sprint.json`
   - `tasks/active/HAK-AI-sprint.json`
3. **Bạn gán người** vào field `assigned_to` (sửa JSON hoặc bảo AI điền theo tên bạn chỉ định).
4. Review `dev_prompt` + `verify_commands` của vài task critical.
5. Revise nếu cần → Approve → gõ `/hackathon-go`.

### Kết quả đạt được

| Có file | Nội dung |
|---------|----------|
| `HAK-*-sprint.json` | Task ≤3h · depends_on · files_to_create · **dev_prompt** · verify_commands · done_when |
| Track INDEX | Task map đã sync |
| `REPO-INDEX.md` | Phase = 6 · task board |

### HITL — bạn duyệt gì?

```
□ Mỗi task có verify đo được không?
□ dev_prompt có bắt đầu bằng đọc INDEX không?
□ assigned_to đã có tên người thật chưa?  ← bắt buộc trước khi code
□ Có task nào nên bỏ / gộp để kịp demo không?
→ /hackathon-go chỉ sau khi bạn đã assign.
```

---

# BƯỚC 7 — Execute · Vai AI: DEV · Bạn: Verify gate

Mỗi track mở **1 chat riêng**. Paste Prompt Phase 7 đúng track **một lần** (trong `WORKFLOW.md`).

| Track | Prompt | INDEX đọc trước |
|-------|--------|-----------------|
| BE | Prompt session BE | `BE-INDEX.md` |
| FE | Prompt session FE | `FE-INDEX.md` |
| AI | Prompt session AI Eng | `AI-INDEX.md` |

### Vòng lặp 1 task (lặp đến hết track)

```
1. AI báo: "Đang task X — đọc Y — sẽ ghi Z"
2. AI viết code đúng path INDEX / LL design
3. AI đưa verify_commands (hoặc tự chạy nếu tool cho phép)
4. ★ HITL: Bạn chạy verify / đọc output / quyết định
5. Pass → bạn gõ /done [id] hoặc "verify pass, /done"
   Fail → "fix theo lỗi: …" (không /done)
6. AI cập nhật INDEX → báo task kế
7. ★ HITL: Bạn gõ "tiếp" (cho phép auto-next) hoặc "dừng"
```

### Kết quả đạt được (mỗi lần `/done`)

| Cập nhật | Ý nghĩa |
|----------|---------|
| Code/file mới đúng path | Deliverable của task |
| Task `status=done` trong JSON | Task đóng chính thức |
| Inventory: PLANNED → NEW | Bản đồ repo cập nhật |
| Current focus = task kế | Session không lạc |
| REPO-INDEX task board | Cả team thấy tiến độ |

### Kết quả hết track

```
AI in: TRACK COMPLETE
□ Bảng task done
□ File/demo liên quan track
□ Blockers còn lại (nếu có)
```

### HITL — bạn duyệt gì mỗi task?

```
□ Verify thật sự pass? (không tin lời AI nếu chưa thấy output)
□ Code có đúng scope task không? (không phình kiến trúc)
□ Có cần /block vì thiếu API/key/người không?
□ Cho phép "tiếp" hay dừng để sync team?
```

**Bạn là cổng `/done`.** Không verify → không done.

---

# BƯỚC 8 — Tích hợp & Demo (HITL cuối)

### Bạn làm gì

1. Khi BE core loop sẵn: bảo FE chạy task switch mock → real API.
2. Chạy end-to-end: user gửi tin → AI trả / escalate.
3. Cắt polish nếu trễ; giữ Must Have đã Approve ở Bước 1.
4. Chuẩn bị demo + slide theo tiêu chí chấm trong brief.

### Kết quả đạt được

```
□ Core loop live (mục tiêu H+12)
□ Domain Must Have demo được
□ REPO-INDEX phản ánh đúng phase execute / done
□ Team biết blocker còn lại trước giờ trình bày
```

---

## Bảng tra nhanh: Sau mỗi lần Enter / Approve

| Lần | Bạn Enter gì | AI làm | Bạn HITL | Kết quả (file / trạng thái) |
|-----|--------------|--------|----------|------------------------------|
| 0 | (tự điền file) | — | Điền brief + PROJECT | Input sẵn |
| 1 | Prompt P1 | Viết Domain Pack | Review MVP → Approve | `hackathon-domain-pack.md` |
| 2 | Prompt P2 | Viết Module Specs | Review map MH→module → Approve | `hackathon-module-specs.md` |
| 3 | Prompt P3 | HL + seed INDEX | Review folder/arch → Approve | `hl-design` + `*-INDEX` |
| 4 | Prompt P4 | LL + path | Review schema/path → Approve | `ll-design` + path map |
| 5 | Prompt P5 | Impl plan | Review milestone → Approve | `impl-plan.md` |
| 6 | Prompt P6 | Task JSON | Assign + Approve → `/hackathon-go` | `HAK-*.json` |
| 7a | Prompt P7 (1 lần) | Code task 1 | Verify → `/done` | Code + INDEX cập nhật |
| 7b | `tiếp` | Code task kế | Verify → `/done` | … lặp |
| 7z | — | TRACK COMPLETE | Chọn integrate / demo | Track xong |

Revise bất cứ lúc nào trước Approve: `/hackathon-revise [yêu cầu]`.

---

## Lệnh bạn dùng (HITL)

| Bạn gõ | Nghĩa |
|--------|--------|
| `/hackathon` | Bắt đầu / chạy phase còn thiếu — **vẫn dừng chờ bạn Approve** |
| `/hackathon-status` | Đang ở phase nào, thiếu file gì |
| `/hackathon-revise …` | Sửa output — chưa Approve |
| `/hackathon-approve` | **Bạn** chốt phase → cho phép phase sau |
| `/hackathon-go` | **Bạn** đã assign → mở Execute |
| `/done [id]` | **Bạn** xác nhận verify pass → đóng task |
| `/block [id] [lý do]` | **Bạn** / AI báo kẹt cần người |
| `tiếp` | Cho phép DEV làm task kế |
| `dừng` / `pause` | Dừng auto-next — chờ sync người |

---

## Checklist một trang (in ra)

### Trước giờ G
```
□ PROJECT.md đã điền
□ hackathon-brief.md đã điền
□ Biết copy Prompt từ WORKFLOW.md
□ Biết: không Approve khi chưa mở file
```

### Planning (Bước 1–6)
```
□ P1 Domain — đã đọc + Approve
□ P2 Modules — đã đọc + Approve
□ P3 HL — đã đọc + Approve
□ P4 LL — đã đọc + Approve
□ P5 Plan — đã đọc + Approve
□ P6 Tasks — đã assign + Approve + /hackathon-go
```

### Execute (Bước 7)
```
□ Session BE / FE / AI đã paste P7
□ Mỗi /done đều có verify thật
□ REPO-INDEX / track INDEX đang đúng Current focus
□ Biết "tiếp" vs "dừng"
```

---

## Milestone giờ vàng (bạn can thiệp nếu trễ)

| Giờ | Phải đạt | HITL nếu trễ |
|-----|----------|--------------|
| H+1 | Domain approved | Cắt Must Have ngay |
| H+2 | Modules approved | Gộp module |
| H+3 | HL+LL approved | Đơn giản hóa folder |
| H+4 | Tasks assigned, DEV code | Bỏ Nice-to-Have khỏi JSON |
| H+12 | Core loop live | Cắt admin/polish |
| H+36 | Integrate | Mock còn lại → ghi rõ trong demo |
| H+44 | Demo ready | Freeze code, chỉ fix crash |

Ưu tiên cắt: **Core loop > Domain > Admin UI > Polish** — quyết định cắt **là của bạn**, không phải AI.

---

*File này = playbook người vận hành + HITL. Prompt dài chỉ trong `WORKFLOW.md`.*
