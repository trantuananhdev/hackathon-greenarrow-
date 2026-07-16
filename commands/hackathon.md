# /hackathon — Phòng IT bằng prompt (48h)

**Usage:** `/hackathon` hoặc `/hackathon [đề bài]`

## Ý tưởng

```
Đề bài → BA → CTO → Tech Lead → DEV
Bạn chỉ: Enter + Review + Approve
```

## SSOT

| Việc | File |
|------|------|
| Prompt từng vai/phase | `WORKFLOW.md` |
| **Hướng dẫn master** | `docs/onboarding/HUONG-DAN-SU-DUNG.md` |
| Hướng dẫn step-by-step | `docs/onboarding/HACKATHON-GUIDE.md` |
| Cheat sheet | `HACKATHON-DAY.md` |
| Điều phối | `skills/hackathon-sprint/SKILL.md` |

## Flow Enter

```
/hackathon
  → BA: Domain → /hackathon-approve
  → BA: Module Specs → /hackathon-approve
  → CTO: HL Design → /hackathon-approve
  → CTO: LL Design → /hackathon-approve
  → TL: Impl Plan → /hackathon-approve
  → TL: Tasks → assign → /hackathon-go
  → DEV: paste Prompt Phase 7 (BE/FE/AI) → /done từng task
```

Hoặc copy từng khối Prompt trong `WORKFLOW.md` (không cần slash).

## Sub-commands

| Command | Action |
|---------|--------|
| `/hackathon` | Phase tiếp theo còn thiếu |
| `/hackathon [đề bài]` | Ghi brief → Phase 1 (BA) |
| `/hackathon-approve` | Approve → chạy vai/phase kế |
| `/hackathon-revise [yêu cầu]` | Sửa output phase hiện tại |
| `/hackathon-status` | Phase + file đã có |
| `/hackathon-go` | Mở Execute (DEV) |
