# Pattern: Hackathon Enter liên tục

**When:** Đề bài 48h → cần BA→CTO→TL→DEV mà human chỉ Enter + Review  
**Reuse:** Mỗi lần chạy `/hackathon` hoặc copy Prompt từ WORKFLOW.md

## Rules

1. **INPUT duy nhất:** `docs/PRD/hackathon-brief.md` + `architecture/PROJECT.md` đã điền thật.
2. **Phase 1–6:** một chat planning; sau mỗi phase human Approve — không skip.
3. **Phase 7:** paste Prompt track **một lần**; sau `/done` AI **auto-next** task kế đến hết JSON.
4. **SSOT prompts:** chỉ `WORKFLOW.md` — không nhân bản prompt sang skill/command.
5. **Path:** Execute chỉ CREATE/EDIT path có trong INDEX / LL design.
6. **Guide:** `docs/onboarding/HUONG-DAN-SU-DUNG.md`

## Anti-patterns

- Paste lại Prompt P7 mỗi task → gãy vòng Enter
- PROJECT.md trống → AI bịa stack/folder
- Skip Approve Phase 1–6 → MVP/path sai, code hàng loạt sai
