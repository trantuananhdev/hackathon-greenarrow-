# 📋 Hackathon Brief — Nơi Đặt Đề Bài

> **ĐÂY LÀ FILE ĐẦU VÀO DUY NHẤT BẠN CẦN ĐIỀN.**
> Hướng dẫn master: `docs/onboarding/HUONG-DAN-SU-DUNG.md`  
> Sau khi điền → `/hackathon` hoặc copy Prompt Phase 1 (`WORKFLOW.md`) → Enter.  
> Luồng: **BA → CTO → Tech Lead → DEV** — bạn chỉ Review → `/hackathon-approve`.

---

## ✍️ HƯỚNG DẪN SỬ DỤNG (3 bước)

```
Bước 1: Xóa các dòng [PLACEHOLDER] bên dưới
Bước 2: Paste/điền đề bài thực tế của BTC vào đúng section
Bước 3: Đọc docs/onboarding/HACKATHON-GUIDE.md → /hackathon
```

---

## 🎯 SECTION 1 — ĐỀ BÀI GỐC TỪ BTC

> Paste toàn bộ nội dung đề bài / problem statement từ Ban Tổ Chức vào đây.
> Có thể paste nguyên văn, không cần format lại.

```
[PASTE TOÀN BỘ ĐỀ BÀI TỪ BAN TỔ CHỨC VÀO ĐÂY]
```

---

## 🏷️ SECTION 2 — THÔNG TIN CƠ BẢN

| Thông tin | Giá trị |
|-----------|---------|
| Tên track / chủ đề | `[VD: AI for Banking / Healthcare AI / ...]` |
| Bài toán cốt lõi | `[VD: Tư vấn tín dụng tự động cho khách hàng SME]` |
| Đối tượng người dùng | `[VD: Khách hàng cá nhân / Nhân viên ngân hàng / ...]` |
| Thời gian thi | `[VD: 48h — 17/7 8:00 → 19/7 8:00]` |
| Số lượng thành viên | `[VD: 5 người]` |

---

## 📊 SECTION 3 — TIÊU CHÍ CHẤM ĐIỂM

> Điền tiêu chí chấm từ BTC để AI ưu tiên build đúng thứ quan trọng nhất.

```
[PASTE TIÊU CHÍ CHẤM ĐIỂM TỪ BTC VÀO ĐÂY]

Ví dụ format:
- Innovation (30%): Tính sáng tạo của giải pháp
- Technical (30%): Chất lượng kỹ thuật, hoàn thiện
- Impact (25%): Tác động kinh doanh thực tế
- Presentation (15%): Demo và thuyết trình
```

---

## ⚠️ SECTION 4 — RÀNG BUỘC KỸ THUẬT (nếu có)

> BTC có yêu cầu bắt buộc nào về tech stack, API, dataset không?

```
[PASTE YÊU CẦU KỸ THUẬT ĐẶC BIỆT VÀO ĐÂY — hoặc ghi "Không có"]

Ví dụ:
- Phải dùng API của nhà tài trợ X
- Dataset được cung cấp: [link]
- Phải deploy được trên cloud Y
- Không được dùng API OpenAI
```

---

## 💡 SECTION 5 — GÓC NHÌN CỦA TEAM (tùy chọn)

> Bổ sung insight của team: hướng tiếp cận ban đầu, competitive advantage, insight từ domain...

```
[GHI GÓC NHÌN, ĐỊNH HƯỚNG, HOẶC INSIGHT BAN ĐẦU CỦA TEAM — có thể bỏ trống]

Ví dụ:
- Chúng ta có người biết domain ngân hàng → tập trung vào compliance
- Competitor thường làm chatbot đơn giản → ta làm reasoning trace visible
- Điểm mạnh: core platform đã có sẵn → tiết kiệm 8h infrastructure
```

---

## 🏗️ SECTION 6 — CORE PLATFORM (tham khảo)

> Đề bài gắn lên **Core Platform** đã có (xem `architecture/PROJECT.md`).
> Pipeline chỉ định nghĩa domain + design + tasks — **không rebuild infrastructure**.

Stack thật của repo: đọc `architecture/PROJECT.md` (không đoán).

---

## 🚀 SAU KHI ĐIỀN XONG

```
Đọc: docs/onboarding/HACKATHON-GUIDE.md
Rồi: /hackathon

→ BA: Domain → approve → Module Specs → approve
→ CTO: HL Design → approve → LL Design → approve
→ TL: Impl Plan → approve → Tasks → assign → /hackathon-go
→ DEV: Prompt Phase 7 (BE/FE/AI) → /done

SSOT prompts: WORKFLOW.md | Cheat: HACKATHON-DAY.md
```

---
*INPUT only. Outputs theo WORKFLOW.md (domain → modules → hl/ll → plan → tasks → INDEX).*

