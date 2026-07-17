# ADR-003 — Parquet cho dữ liệu thời tiết lịch sử

**Status:** ✅ Accepted  
**Date:** 2026-07-17  
**Proposed by:** Human + AI  
**Related OKR:** Hackathon weather analysis

---

## Context

Hệ thống cần lưu 10 năm dữ liệu thời tiết theo giờ cho 85 điểm tại Điện Biên,
tương đương 7.452.120 bản ghi. SQLite và một DataFrame duy nhất không phù hợp
cho việc tải resume, quét theo năm và xử lý ngoài bộ nhớ.

## Decision

We will **lưu danh mục địa danh và dữ liệu lịch sử bằng Parquet phân vùng theo
năm; fact thời tiết chỉ giữ `location_id` để join với danh mục địa danh**
because **cách này nén tốt, đọc chọn lọc và tránh nhân bản dữ liệu địa danh trên
hàng triệu dòng**.

## Options Considered

### Option A: SQLite
- ✅ Pros: Truy vấn SQL quen thuộc, một file.
- ❌ Cons: Ghi/tải hàng triệu dòng chậm hơn, khó phân vùng và resume theo part.

### Option B: Parquet phân vùng theo năm ← Selected
- ✅ Pros: Nén cột tốt, đọc chọn lọc, hỗ trợ dataset lớn ngoài RAM.
- ❌ Cons: Cần manifest và verify gate riêng; join tên địa danh qua `location_id`.

### Option C: CSV
- ✅ Pros: Dễ xem bằng công cụ phổ thông.
- ❌ Cons: Dung lượng lớn, mất kiểu dữ liệu và timezone, đọc chậm.

## Consequences

**Positive:**
- Dataset có thể resume và kiểm tra theo part.
- Không lặp tên hành chính/tọa độ yêu cầu trên 7,45 triệu fact.
- PyArrow có thể query preview mà không nạp toàn bộ dataset.

**Negative / Trade-offs:**
- Người dùng phải join với `dien_bien_locations.parquet` để xem tên địa danh.
- Cần giữ fingerprint cấu hình trong `_manifest.json`.

**Neutral:**
- ERA5 được dùng thống nhất cho giai đoạn 2016–2025 để có đủ biến mưa và gió.

## Implementation Plan

```text
1. Tạo dien_bien_locations.parquet với location_id ổn định.
2. Tải ERA5 theo năm/lô và atomic-write các part.
3. Verify đủ 50 part, 85 điểm và 7.452.120 dòng.
4. Notebook đọc dataset qua PyArrow và join danh mục khi cần.
```

## Links

- Task: WEATHER-HISTORY-001
