# 🔄 WORKFLOW — Hackathon 48h (SSOT)

> **Phòng IT bằng prompt:** bạn chỉ đưa đề bài → Enter liên tục.  
> Mỗi phase = **một vai** (BA → CTO → Tech Lead → DEV). AI tự đọc/ghi file.  
> Bạn = Product Owner: **Review → Approve** (hoặc gõ `/hackathon-approve`).  
> Phase 7: paste Prompt **một lần** → `/done` → **auto-next** đến hết track.  
> Prompt nằm dưới đây — **không** nhân bản sang file khác.  
> Hướng dẫn master: `docs/onboarding/HUONG-DAN-SU-DUNG.md`

---

## PHÒNG IT — AI ĐÓNG VAI LẦN LƯỢT

```
HUMAN          đưa đề bài vào docs/PRD/hackathon-brief.md
    │
    ▼  Enter Prompt P1–P2
BA             Domain Pack + Module Specs          ✋ Review
    │
    ▼  Enter Prompt P3–P4
CTO            HL Design + LL Design               ✋ Review
               (kèm folder FE/BE + INDEX repo)
    │
    ▼  Enter Prompt P5–P6
TECH LEAD      Impl Plan + Task breakdown          ✋ Review → Assign
    │
    ▼  Enter Prompt P7 (mỗi DEV 1 session)
DEV            BE / FE / AI code theo task          ✅ /done + cập nhật INDEX
```

---

## PIPELINE (= từng lần Enter)

| Enter # | Vai | Phase | Output chính |
|---------|-----|-------|--------------|
| 1 | **BA** | Domain Pack | `docs/PRD/hackathon-domain-pack.md` |
| 2 | **BA** | Module Specs | `docs/design/hackathon-module-specs.md` |
| 3 | **CTO** | High-Level Design | `hackathon-hl-design.md` + seed INDEX |
| 4 | **CTO** | Low-Level Design | `hackathon-ll-design.md` + path trong INDEX |
| 5 | **Tech Lead** | Impl Plan | `hackathon-impl-plan.md` |
| 6 | **Tech Lead** | Tasks | `HAK-{BE,FE,AI}-sprint.json` |
| 7+ | **DEV** | Execute | code + `/done` + INDEX |

Sau mỗi Enter 1–6: đọc checklist → OK thì **Approve** → copy prompt phase kế → Enter lại.

Hướng dẫn người mới (step-by-step + HITL): `docs/onboarding/HUONG-DAN-SU-DUNG.md`  
Cheat sheet: `HACKATHON-DAY.md` · Lệnh: `commands/hackathon.md` · Chi tiết cũ: `HACKATHON-GUIDE.md`

---

## BẢN ĐỒ FILE

| Phase | ĐỌC | VIẾT |
|-------|-----|------|
| 0 | — | điền `docs/PRD/hackathon-brief.md` |
| 1 | brief + `architecture.md` + `architecture/PROJECT.md` | `docs/PRD/hackathon-domain-pack.md` |
| 2 | domain-pack + architecture.md + PROJECT.md | `docs/design/hackathon-module-specs.md` |
| 3 | domain-pack + module-specs + architecture.md + PROJECT.md + **scan repo** | `hackathon-hl-design.md` + seed `REPO/BE/FE/AI-INDEX.md` |
| 4 | hl + module-specs + domain-pack + indexes + architecture | `hackathon-ll-design.md` + **cập nhật** BE/FE/AI-INDEX (path chi tiết) |
| 5 | hl + ll + module-specs + indexes | `hackathon-impl-plan.md` |
| 6 | module-specs + ll + impl-plan + indexes | `HAK-{BE,FE,AI}-sprint.json` + **task map trong indexes** |
| 7 | **track INDEX trước** → task JSON → ll-design | code + `/done` + **cập nhật INDEX** |

### Index files (bản đồ sống — Execute đọc trước)

| File | Dùng cho |
|------|----------|
| `docs/design/REPO-INDEX.md` | Toàn repo: đang ở phase/task nào, đọc gì tiếp |
| `docs/design/BE-INDEX.md` | Backend: folder, inventory, module→path, task map |
| `docs/design/FE-INDEX.md` | Frontend: tương tự |
| `docs/design/AI-INDEX.md` | Agent/RAG/prompts: tương tự |

---

## PHASE 0 — CHUẨN BỊ

```
□ Điền docs/PRD/hackathon-brief.md (đề bài BTC)
□ architecture.md = core platform (nếu có trong repo)
□ architecture/PROJECT.md = stack + convention thật
□ Templates index sẵn: docs/design/{REPO,BE,FE,AI}-INDEX.md
□ Docker / local run được (nếu có)
□ Mỗi người 1 AI session
□ Phân vai: Team Lead | BE1 | BE2 | FE | AI Eng
```

---

## PHASE 1 — DOMAIN PACK · Vai: BA

**Mục đích:** Chốt bài toán MVP 48h — features, stories, rules, tools.  
**Approve khi:** 3–5 Must Have demo được trong 48h.  
**Prompt kế:** Phase 2 (vẫn vai BA).

### Prompt — copy nguyên khối

```
VAI TRÒ: BA (Business Analyst) trong phòng IT hackathon 48h.
Bạn nhận handoff từ Human (đề bài). Tự đọc file, tự viết file, không hỏi lại trừ khi thiếu đề bài.
Sau khi xong: đưa checklist review cho Product Owner — chờ Approve rồi mới sang Phase 2.

## ĐỌC (bắt buộc, theo thứ tự)
1. docs/PRD/hackathon-brief.md
2. architecture.md (core platform — nếu file tồn tại)
3. architecture/PROJECT.md

## VIẾT (ghi đè / tạo mới)
docs/PRD/hackathon-domain-pack.md

## NỘI DUNG BẮT BUỘC trong file output

### 1. PRD MVP 48h
- Mục tiêu demo 1 câu
- 3–5 Must Have + bảng Must / Should / Nice-to-Have
- Vì sao KHÔNG làm các mục ngoài Must Have

### 2. User Stories
- End-user (chat / web)
- Admin / Staff
Format: Là [role], tôi muốn [action] để [value]

### 3. Business Rules
- Intent taxonomy
- Escalation (threshold, keyword, điều kiện)
- Confidence + fallback

### 4. Domain Tools
| Tool | Mô tả | Input | Output | Stub trong 48h? |

### 5. Seed Data
- Docs RAG cần nạp
- Intents / playbooks
- Hướng system prompt (tone, constraint)

## RÀNG BUỘC
- Không đổi kiến trúc core đã có trong PROJECT.md — chỉ định nghĩa domain layer
- Ngắn, dùng bảng; kết thúc file bằng dòng:
  ✅ Domain Pack hoàn thành. Sẵn sàng Phase 2 — Module Specs.

Sau khi ghi file xong, in checklist review ngắn (5 bullet) để human approve.
```

### ✋ Review 1
```
□ Must Have demo được trong 48h?
□ Stories / rules / tools đủ cho MVP?
→ Revise hoặc Approve → Phase 2
```

---

## PHASE 2 — MODULE SPECS · Vai: BA

**Mục đích:** Liệt kê module cần build từ Domain — trách nhiệm, I/O, priority.  
**Chưa** đi sâu logic nội bộ (đó là CTO Phase 4).  
**Approve khi:** danh sách module + biên giới rõ.  
**Prompt kế:** Phase 3 — chuyển vai **CTO**.

### Prompt — copy nguyên khối

```
VAI TRÒ: BA (Business Analyst) — Phase 2 Module Specs.
Handoff từ Domain Pack (đã approve). Tự đọc file, tự viết file.
Sau khi xong: checklist cho PO. Approve xong → phòng IT chuyển sang CTO (Phase 3).

## ĐỌC
1. docs/PRD/hackathon-domain-pack.md
2. architecture.md (nếu có)
3. architecture/PROJECT.md

## VIẾT
docs/design/hackathon-module-specs.md

## NỘI DUNG BẮT BUỘC

### 1. Module Inventory
Bảng:
| Module ID | Tên | Layer (BE/FE/AI/Shared) | [EXISTING]/[NEW]/[EXTERNAL] | Priority | Owner gợi ý |

### 2. Spec từng [NEW] module (ngắn — chưa low-level)
Với mỗi module NEW:
- Trách nhiệm (1–2 câu)
- Input / Output (format mức contract)
- Phụ thuộc module nào
- Liên hệ feature Must Have nào trong Domain Pack
- Out of scope (cái không làm trong 48h)

### 3. Gap vs Core
- Core đã có gì → tái dùng
- Cần build mới gì → list

Kết thúc file:
✅ Module Specs hoàn thành. Sẵn sàng Phase 3 — High-Level System Design.

In checklist review ngắn cho human.
```

### ✋ Review 2
```
□ Mọi Must Have đều map vào ≥1 module?
□ Không trùng trách nhiệm giữa module?
→ Revise hoặc Approve → Phase 3
```

---

## PHASE 3 — HIGH-LEVEL SYSTEM DESIGN · Vai: CTO

**Mục đích:** Component, data flow, contracts + **folder structure FE & BE** + seed index.  
**Approve khi:** cây thư mục target rõ; index phản ánh repo hiện có.  
**Prompt kế:** Phase 4 (vẫn vai CTO).

### Prompt — copy nguyên khối

```
VAI TRÒ: CTO / Principal Architect trong phòng IT hackathon 48h.
Handoff từ BA (Domain Pack + Module Specs đã approve).
Tự đọc file, tự scan repo, tự viết file. Không hỏi path nếu liệt kê được từ disk.
Sau khi xong: checklist cho PO — chờ Approve rồi Phase 4 (vẫn CTO).

## ĐỌC
1. docs/PRD/hackathon-domain-pack.md
2. docs/design/hackathon-module-specs.md
3. architecture.md (nếu có)
4. architecture/PROJECT.md
5. docs/design/REPO-INDEX.md (template)
6. SCAN repo: liệt kê thư mục/file quan trọng hiện có (BE root, FE root, agent/, data/, docker…)

## VIẾT (tất cả các file sau)
1. docs/design/hackathon-hl-design.md
2. docs/design/REPO-INDEX.md  (cập nhật phase=3, folder tóm tắt, đọc-gì bảng)
3. docs/design/BE-INDEX.md    (seed: folder target + Inventory EXISTING từ scan)
4. docs/design/FE-INDEX.md    (seed tương tự)
5. docs/design/AI-INDEX.md    (seed tương tự)

## NỘI DUNG BẮT BUỘC trong hackathon-hl-design.md

### 1. Component Diagram
- Mermaid hoặc text art
- [EXISTING] / [NEW] / [EXTERNAL]

### 2. Data Flow (≥3 luồng demo)

### 3. Interface Contracts
| From | To | Protocol | Message shape |

### 4. Data model overview (chưa field-level)

### 5. Folder Structure — Backend (BẮT BUỘC)
Cây thư mục TARGET đầy đủ (monolith hoặc services), ví dụ mức:
app/routers, services, models, agent, tools, repositories…
Với mỗi folder: 1 dòng mục đích + gắn Module ID từ module-specs
Đánh dấu folder [EXISTING] vs [NEW]

### 6. Folder Structure — Frontend (BẮT BUỘC)
Cây TARGET: app/ hoặc src/ — routes, components, hooks, stores, api client, mocks…
Mỗi folder: mục đích + Module ID
[EXISTING] vs [NEW]

### 7. Folder Structure — AI / data (nếu tách)
prompts, playbooks, knowledge, evals…

### 8. NFR + Risk Register

## NỘI DUNG BẮT BUỘC trong BE-INDEX / FE-INDEX / AI-INDEX
- Folder structure (copy từ HL)
- Inventory: mọi path EXISTING đã scan + path PLANNED quan trọng từ cây TARGET
- Current focus = none (chưa execute)
- Read guide giữ nguyên / bổ sung path thật

## REPO-INDEX
- Pipeline phase = 3
- Điền tóm tắt folder + bảng “Đọc gì”

Kết thúc:
✅ HL Design + Folder Structure + Index seed hoàn thành. Sẵn sàng Phase 4.

In checklist review ngắn cho human.
```

### ✋ Review 3
```
□ Diagram + flow đủ chia track?
□ Cây FE + BE rõ, khớp module-specs?
□ Index Inventory phản ánh đúng repo hiện có?
→ Revise hoặc Approve → Phase 4
```

---

## PHASE 4 — LOW-LEVEL SYSTEM DESIGN · Vai: CTO

**Mục đích:** Chi tiết implement + **map module → file path**; cập nhật INDEX.  
**Approve khi:** mỗi module NEW có path; Module→Path đủ dùng.  
**Prompt kế:** Phase 5 — chuyển vai **Tech Lead**.

### Prompt — copy nguyên khối

```
VAI TRÒ: CTO / Senior Architect — Low-Level Design (Phase 4).
Handoff từ HL Design + folder structure (đã approve).
Tự đọc file, tự viết file. Path phải khớp Folder Structure Phase 3.
Sau khi xong: checklist cho PO. Approve → chuyển Tech Lead (Phase 5).

## ĐỌC
1. docs/design/hackathon-hl-design.md
2. docs/design/hackathon-module-specs.md
3. docs/PRD/hackathon-domain-pack.md
4. docs/design/BE-INDEX.md
5. docs/design/FE-INDEX.md
6. docs/design/AI-INDEX.md
7. architecture.md (nếu có)
8. architecture/PROJECT.md

## VIẾT
1. docs/design/hackathon-ll-design.md
2. Cập nhật docs/design/BE-INDEX.md
3. Cập nhật docs/design/FE-INDEX.md
4. Cập nhật docs/design/AI-INDEX.md
5. Cập nhật docs/design/REPO-INDEX.md (phase=4)

## NỘI DUNG BẮT BUỘC trong hackathon-ll-design.md

Với MỖI module [NEW]:

### Module: [ID] [Tên]
- Layer: BE | FE | AI
- Trách nhiệm
- Input / Output schema (field + type)
- Internal logic (steps / pseudo-code)
- State machine (nếu có)
- Error cases
- DB / API (nếu có) — Method Path request/response
- External calls
- **Files (BẮT BUỘC):**
  | Action | Path | Mô tả |
  | CREATE/EDIT | đúng cây HL | …
- Constraints

### Cross-cutting
- Auth, error JSON, logging tối thiểu
- Quy ước import / barrel files nếu FE cần

## CẬP NHẬT INDEXES (BẮT BUỘC)
- Section Module → Path: đủ mọi module NEW
- Inventory: thêm mọi path CREATE ở trên với Status=PLANNED
- Read guide: bổ sung “implement module X → đọc LL section Y + path Z”

Kết thúc:
✅ LL Design + Index path map hoàn thành. Sẵn sàng Phase 5.

In checklist review ngắn cho human.
```

### ✋ Review 4
```
□ Mỗi module NEW có schema + file path cụ thể?
□ Path nằm đúng cây FE/BE Phase 3?
□ BE/FE/AI-INDEX Module→Path đủ?
→ Revise hoặc Approve → Phase 5
```

---

## PHASE 5 — IMPLEMENTATION PLAN · Vai: Tech Lead

**Mục đích:** Thứ tự, parallel tracks, milestone, critical path.  
**Approve khi:** cả team đồng ý thứ tự làm.  
**Prompt kế:** Phase 6 (vẫn Tech Lead).

### Prompt — copy nguyên khối

```
VAI TRÒ: Tech Lead / Engineering Manager trong phòng IT hackathon 48h.
Handoff từ CTO (HL + LL + INDEX đã approve).
Tự đọc file, tự viết file.
Sau khi xong: checklist cho PO — Approve rồi Phase 6 (vẫn Tech Lead).

## ĐỌC
1. docs/design/hackathon-hl-design.md
2. docs/design/hackathon-ll-design.md
3. docs/design/hackathon-module-specs.md
4. docs/design/BE-INDEX.md
5. docs/design/FE-INDEX.md

## VIẾT
docs/design/hackathon-impl-plan.md
(+ cập nhật REPO-INDEX phase=5)

## CONSTRAINTS
- Team ~5: TL, BE1, BE2, FE, AI Eng
- Tổng 48h; gate: core loop (tin vào → AI trả) xong ≤ H+12
- FE mock trước, switch real API khi BE sẵn

## NỘI DUNG BẮT BUỘC

### 1. Dependency Graph + Critical Path
### 2. Parallel Tracks (BE-Core / BE-Domain / FE / AI)
### 3. Integration Points | Giờ | Track A | Track B | Sync |
### 4. Milestone Gates
| Milestone | Giờ | Pass khi | Fail thì |
Gợi ý: H+4 plan+tasks | H+12 core loop | H+24 domain | H+36 integrate | H+44 demo
### 5. Timebox | Module | Owner | Estimate | Buffer |
### 6. Risk → action cụ thể nếu xảy ra

Kết thúc file:
✅ Impl Plan hoàn thành. Sẵn sàng Phase 6 — Tasks.

In checklist review ngắn cho human.
```

### ✋ Review 5
```
□ Critical path đúng?
□ Track song song không đụng nhau?
□ Timebox thực tế với team?
→ Revise hoặc Approve → Phase 6
```

---

## PHASE 6 — TASKS · Vai: Tech Lead

**Mục đích:** Task ≤3h + `dev_prompt` trỏ INDEX; cập nhật task map.  
**Approve khi:** assign xong → `/hackathon-go` hoặc paste Prompt Phase 7.  
**Prompt kế:** Phase 7 — chuyển vai **DEV** (BE / FE / AI, mỗi người 1 session).

### Prompt — copy nguyên khối

```
VAI TRÒ: Tech Lead / Scrum Master — Task breakdown (Phase 6).
Handoff từ Impl Plan (đã approve).
Tự đọc file, tự viết JSON + cập nhật indexes.
Sau khi xong: PO assign người vào assigned_to → /hackathon-go → DEV sessions.

## ĐỌC
1. docs/design/hackathon-module-specs.md
2. docs/design/hackathon-ll-design.md
3. docs/design/hackathon-impl-plan.md
4. docs/design/BE-INDEX.md
5. docs/design/FE-INDEX.md
6. docs/design/AI-INDEX.md
7. docs/design/REPO-INDEX.md

## VIẾT
1. tasks/active/HAK-BE-sprint.json
2. tasks/active/HAK-FE-sprint.json
3. tasks/active/HAK-AI-sprint.json
4. Cập nhật Task map + (tuỳ chọn) Current focus=next critical trên BE/FE/AI-INDEX
5. REPO-INDEX: phase=6, task board

## SCHEMA MỖI TASK (bắt buộc đủ field)
{
  "id": "BE-01",
  "name": "...",
  "priority": "critical|high|medium",
  "depends_on": [],
  "timebox_hours": 2,
  "assigned_to": null,
  "description": "...",
  "output": "đầu ra đo được",
  "files_to_create": [],
  "files_to_read": [
    "docs/design/BE-INDEX.md",
    "docs/design/hackathon-ll-design.md → Module X"
  ],
  "dev_prompt": "BẮT BUỘC mở đầu bằng: (1) đọc track INDEX Current focus + Inventory (2) đọc LL section module (3) chỉ CREATE/EDIT đúng path trong INDEX. Sau đó: role, schema, output, verify. Đủ để Enter một phát.",
  "verify_commands": [],
  "done_checklist": [
    "đúng path trong BE/FE/AI-INDEX",
    "verify_commands pass",
    "đã cập nhật INDEX (Inventory + Task map) sau khi xong",
    "done_when đạt"
  ],
  "done_when": "điều kiện đo được",
  "status": "todo",
  "index_ref": "docs/design/BE-INDEX.md"
}

## QUY TẮC
- files_to_read luôn gồm track INDEX tương ứng
- Path trong files_to_create phải có trong INDEX Inventory (PLANNED) hoặc LL design
- Root JSON: { "sprint": "HAK", "track": "BE|FE|AI", "tasks": [ ... ] }

Kết thúc:
✅ Tasks + Index task map hoàn thành. Assign rồi /hackathon-go.

In bảng tóm tắt task cho human.
```

### ✋ Review 6 + Assign
```
□ dev_prompt bắt đầu bằng đọc INDEX?
□ Path khớp BE/FE folder structure?
□ Gán assigned_to
→ /hackathon-go → Phase 7
```

---

## PHASE 7 — EXECUTE · Vai: DEV (BE / FE / AI)

> Không quyết định kiến trúc nữa.  
> **Luôn:** INDEX → `dev_prompt` → code → verify → `/done` → **tự nhảy task kế** → lặp đến hết track.  
> Mỗi DEV = 1 AI session riêng. Human chỉ: chạy verify (nếu cần) + gõ `tiếp` / Enter.

### 🔁 Vòng Enter liên tục (bắt buộc sau khi paste Prompt P7 một lần)

```
Paste Prompt P7 (1 lần / session)
    │
    ▼
AI: task N → code → đề xuất verify_commands
    │
    ├─ Human: chạy verify → paste output  (hoặc gõ: "verify pass" nếu AI tự chạy được)
    │
    ▼
AI: /done task N → cập nhật INDEX → Current focus = task N+1
    │
    ▼
Human chỉ cần: Enter hoặc gõ "tiếp"
    │
    ▼
AI: tự làm task N+1 (KHÔNG cần paste lại Prompt P7)
    │
    └─ lặp đến khi track JSON hết todo / blocked

Kết thúc track: AI in "TRACK COMPLETE" + bảng done + file demo.
```

**Quy tắc auto-next:** Sau mỗi `/done` thành công, AI **không dừng chờ prompt mới** — báo task kế và bắt đầu ngay (trừ khi human gõ `dừng` / `pause`).

### Prompt session BE — copy nguyên khối

```
VAI TRÒ: DEV Backend trong phòng IT hackathon 48h.
Handoff từ Tech Lead (task JSON + INDEX đã sẵn).
CHẾ ĐỘ: Enter liên tục — sau /done tự nhảy task kế đến hết HAK-BE-sprint.json.

## ĐỌC (đúng thứ tự — không bỏ)
1. docs/design/REPO-INDEX.md     → đang ở phase/task nào
2. docs/design/BE-INDEX.md       → Current focus, Inventory, Module→Path, Task map
3. tasks/active/HAK-BE-sprint.json
4. docs/design/hackathon-ll-design.md (section của task)
5. architecture/PROJECT.md (+ architecture.md nếu đụng core)

## QUY TRÌNH (1 task)
1. Xác định task: ưu tiên Current focus trên BE-INDEX; nếu none → todo critical đủ depends_on trong JSON
2. Cập nhật BE-INDEX Current focus = task đó, status=in_progress; sync REPO-INDEX
3. Làm đúng dev_prompt; chỉ ghi path có trong INDEX / LL design
4. Chạy verify_commands nếu tool cho phép; không thì đưa lệnh + chờ human paste kết quả
5. Pass → status=done trong JSON; tick done_checklist; Inventory PLANNED→NEW; sync REPO-INDEX
6. Fail → fix; blocked → /block + cập nhật INDEX (rồi chọn task khác đủ depends_on nếu còn)

## AUTO-NEXT (bắt buộc)
7. Sau /done: chọn task kế (priority cao nhất, đủ depends_on, status=todo)
8. Cập nhật Current focus = task kế → báo 1 dòng "➡️ Next: [id] [name]" → BẮT ĐẦU code ngay
9. Chỉ dừng khi: hết todo · tất cả còn lại blocked · human gõ "dừng"/"pause"

BẮT ĐẦU: báo cáo ngắn "Đang ở task X — đọc Y — sẽ ghi Z" rồi code.
```

### Prompt session FE — copy nguyên khối

```
VAI TRÒ: DEV Frontend trong phòng IT hackathon 48h.
Handoff từ Tech Lead. CHẾ ĐỘ: Enter liên tục — /done → auto-next đến hết HAK-FE-sprint.json.

## ĐỌC (đúng thứ tự)
1. docs/design/REPO-INDEX.md
2. docs/design/FE-INDEX.md
3. tasks/active/HAK-FE-sprint.json
4. docs/design/hackathon-ll-design.md (+ hl contracts nếu cần)
5. architecture/PROJECT.md

## QUY TRÌNH
Giống BE nhưng dùng FE-INDEX / HAK-FE-sprint.json.
Mock trước nếu API mode=mock; khi BE ready → task switch-real + API mode=real trên FE-INDEX.
Sau mỗi /done → AUTO-NEXT (giống BE bước 7–9).

BẮT ĐẦU: "Đang ở task X — đọc Y — sẽ ghi Z" rồi code.
```

### Prompt session AI Eng — copy nguyên khối

```
VAI TRÒ: DEV AI Engineer trong phòng IT hackathon 48h.
Handoff từ Tech Lead. CHẾ ĐỘ: Enter liên tục — /done → auto-next đến hết HAK-AI-sprint.json.

## ĐỌC (đúng thứ tự)
1. docs/design/REPO-INDEX.md
2. docs/design/AI-INDEX.md
3. docs/PRD/hackathon-domain-pack.md
4. tasks/active/HAK-AI-sprint.json
5. docs/design/hackathon-ll-design.md
6. architecture.md (agent runtime) + architecture/PROJECT.md

## QUY TRÌNH
Giống BE với AI-INDEX / HAK-AI-sprint.json.
Sau mỗi /done → AUTO-NEXT (giống BE bước 7–9).

BẮT ĐẦU: "Đang ở task X — đọc Y — sẽ ghi Z" rồi giao hàng.
```

### Session mới nhảy vào giữa chừng

```
Chỉ cần:
1. docs/design/REPO-INDEX.md          ← đang đứng đâu
2. docs/design/{BE|FE|AI}-INDEX.md    ← task + path + inventory
3. Paste đúng Dev Session prompt Phase 7 → Enter
   → AI tiếp tục từ Current focus + auto-next đến hết track

(Không cần đọc lại toàn bộ domain/HL trừ khi INDEX bảo Read-first.)
```

---

## MILESTONE

| Giờ | Gate |
|-----|------|
| H+1 | Domain Pack approved |
| H+2 | Module Specs approved |
| H+3 | HL + LL Design approved |
| H+4 | Impl Plan + Tasks assigned — bắt đầu code |
| H+12 | **CORE LOOP LIVE** |
| H+24 | Domain features |
| H+36 | Full integration |
| H+44 | Demo ready |
| H+48 | Present |

Ưu tiên cắt scope: **Core loop > Domain features > Admin UI > Polish**

---

*SSOT vận hành hackathon. Skill/command chỉ trỏ về file này — không nhân bản prompt.*
