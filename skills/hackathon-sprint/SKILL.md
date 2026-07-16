# SKILL: Hackathon Sprint Pipeline
# Trigger: `/hackathon` · "bắt đầu hackathon" · paste đề bài 48h

> **SSOT prompts:** `WORKFLOW.md`  
> **Hướng dẫn master:** `docs/onboarding/HUONG-DAN-SU-DUNG.md`  
> **Hướng dẫn chi tiết:** `docs/onboarding/HACKATHON-GUIDE.md`  
> Skill chỉ **điều phối vai/phase** — không nhân bản prompt.

---

## Phòng IT (logic bắt buộc)

```
Đề bài (Human)
  → BA: Phase 1 Domain, Phase 2 Module Specs
  → CTO: Phase 3 HL, Phase 4 LL (+ folder FE/BE + INDEX)
  → Tech Lead: Phase 5 Impl Plan, Phase 6 Tasks
  → DEV: Phase 7 Execute (BE/FE/AI)
```

Mỗi phase: chạy đúng 1 prompt trong WORKFLOW → dừng cho human approve → phase sau.  
Không skip vai.

---

## Pipeline

```
0 Brief → 1 BA Domain → 2 BA Modules → 3 CTO HL → 4 CTO LL
→ 5 TL Plan → 6 TL Tasks → 7 DEV Execute
```

---

## Khi kích hoạt

1. Đọc `WORKFLOW.md` + `docs/design/REPO-INDEX.md` (nếu có) + `memory/hot/state.json`
2. Xác định phase hiện tại (bảng detect dưới)
3. Chạy **đúng một** prompt phase đó (vai đúng BA/CTO/TL/DEV)
4. Ghi file xong → checklist review — **không** tự Approve sang phase sau

---

## Lệnh

| Command | Action |
|---------|--------|
| `/hackathon` | Phase tiếp theo còn thiếu (thường Phase 1 BA) |
| `/hackathon [đề bài]` | Ghi `hackathon-brief.md` → Phase 1 |
| `/hackathon-approve` | Approve → phase/vai kế |
| `/hackathon-revise [yêu cầu]` | Sửa output phase hiện tại |
| `/hackathon-status` | Phase + vai + file đã có/thiếu |
| `/hackathon-go` | Sau Phase 6 assigned → hướng dẫn Prompt DEV Phase 7 |

---

## Detect phase hiện tại

| File đã có & hợp lệ | Phase tiếp | Vai |
|---------------------|------------|-----|
| chỉ brief | 1 Domain | BA |
| + domain-pack | 2 Module Specs | BA |
| + module-specs | 3 HL Design | CTO |
| + hl-design | 4 LL Design | CTO |
| + ll-design | 5 Impl Plan | TL |
| + impl-plan | 6 Tasks | TL |
| + HAK-*-sprint.json | chờ assign → go → 7 | DEV |
| đang execute | Phase 7 | DEV |

---

## Output files (chuẩn)

```
docs/PRD/hackathon-brief.md
docs/PRD/hackathon-domain-pack.md
docs/design/hackathon-module-specs.md
docs/design/hackathon-hl-design.md
docs/design/hackathon-ll-design.md
docs/design/hackathon-impl-plan.md
docs/design/REPO-INDEX.md
docs/design/BE-INDEX.md
docs/design/FE-INDEX.md
docs/design/AI-INDEX.md
tasks/active/HAK-BE-sprint.json
tasks/active/HAK-FE-sprint.json
tasks/active/HAK-AI-sprint.json
```

Phase 3: folder FE/BE + seed indexes.  
Phase 4: path map vào indexes.  
Phase 7: đọc track INDEX trước task JSON.

---

## Hard rules

1. Không skip human approve giữa phase 1–6
2. Stack từ `architecture.md` + `architecture/PROJECT.md` — không invent
3. `/done` cần verify + cập nhật INDEX
4. Prompt dài chỉ ở `WORKFLOW.md`
5. Execute không invent path ngoài INDEX / LL design
6. Phase 7: sau `/done` **auto-next** task kế (không chờ paste lại Prompt) đến hết track hoặc human `dừng`
