# ADR-004 — Phạm vi 5 năm và phân vùng quý cho dữ liệu thời tiết

**Status:** ✅ Accepted — supersedes phạm vi thời gian, biến và cách phân vùng trong ADR-003
**Date:** 2026-07-17
**Proposed by:** Human
**Related OKR:** Hackathon weather analysis

---

## Context

Pipeline ban đầu tải 85 điểm × 10 năm theo từng năm, tạo payload lớn và bị
Open-Meteo Archive API timeout hoặc HTTP 429. Với hackathon, thời gian tải ổn
định quan trọng hơn việc giữ toàn bộ 10 năm.

## Decision

We will **thu thập ERA5 theo giờ cho 2021–2025, chia mỗi request thành một quý
và tối đa 10 điểm, nghỉ 60 giây giữa request, đồng thời bỏ
`wind_gusts_10m`** because **payload nhỏ hơn và 5 năm gần nhất đủ cho phạm vi
training/evaluation của hackathon**.

## Options Considered

### Option A: 10 năm, request theo năm
- ✅ Pros: Lịch sử dài hơn.
- ❌ Cons: Payload lớn, liên tục timeout/429.

### Option B: 5 năm, request theo quý ← Selected
- ✅ Pros: Payload giảm khoảng 8 lần; resume chi tiết; phù hợp hackathon.
- ❌ Cons: Chỉ còn khoảng 3,73 triệu dòng; tăng số HTTP request.

## Consequences

**Positive:**
- Mỗi part nhỏ hơn và dễ kiểm tra/tải lại.
- Progress có phần trăm và ETA.
- Tổng phạm vi giảm còn 2021–2025.

**Negative / Trade-offs:**
- Không có dữ liệu 2016–2020.
- Không có `wind_gusts_10m`.
- Tổng cộng 180 request nên vẫn cần chạy dài và resume.

## Implementation Plan

```text
1. Phân vùng year=YYYY/q=QX/part-NNN.parquet.
2. Cập nhật manifest, verifier, notebook và automation.
3. Dry-run 2025, sau đó tải thử phạm vi nhỏ.
4. Verify đủ 180 part, 85 điểm và 3.725.040 dòng.
```

## Links

- Supersedes: các quyết định về 10 năm, 8 biến và phân vùng chỉ theo năm trong ADR-003
- Task: WEATHER-HISTORY-001
