# ADR-005 — Ưu tiên vertical slice dự báo và cảnh báo

**Status:** ✅ Accepted — supersedes việc coi ERA5 bulk là điều kiện tiên quyết cho demo
**Date:** 2026-07-17
**Proposed by:** Human

## Context

Pipeline trước tập trung tải 5 năm dữ liệu ERA5 cho 85 điểm. Việc tải mất nhiều
thời gian, phụ thuộc quota và chưa trực tiếp tạo ra luồng cảnh báo có thể demo.

## Decision

Ưu tiên triển khai theo thứ tự:

1. P0 — data contract.
2. P1 — elevation và Open-Meteo forecast snapshot.
3. P2 — tổng hợp chỉ số và sinh cảnh báo MVP.
4. Demo luồng Forecast → Risk → Alert.
5. P3–P7 chỉ cải thiện độ tin cậy sau khi vertical slice hoạt động.

ERA5 bulk 2021–2025 vẫn giữ pipeline Parquet/resume theo ADR-003 và ADR-004,
nhưng chuyển sang backlog và không còn chặn demo.

Forecast dùng `snapshot_at` làm thời điểm chụp dữ liệu. `issued_at` chỉ được
điền khi nguồn cung cấp thời điểm phát hành model thực sự. Dữ liệu enrichment
được tách khỏi locations master.

## Consequences

### Positive

- Có sản phẩm end-to-end để demo sớm.
- Không phụ thuộc việc tải xong 3.725.040 dòng ERA5.
- Mỗi nguồn bổ sung có thể cải thiện hệ thống mà không chặn MVP.

### Trade-offs

- Ngưỡng cảnh báo ban đầu là rule-based và phải ghi rõ giới hạn.
- Chưa có hiệu chỉnh địa phương bằng DesInventar, quan trắc hoặc ERA5 đầy đủ.
- GloFAS, World Bank, OWM và NCHMF được thực hiện sau vertical slice.

## Links

- Plan: `docs/data/weather-alert-pipeline-plan.md`
- Active task: `WEATHER-ALERT-MVP-002`
- Background task: `WEATHER-HISTORY-001`
- Related: ADR-003, ADR-004
