# ADR-006 — Tách data artifact khỏi pipeline code

**Status:** ✅ Accepted
**Date:** 2026-07-17
**Proposed by:** human + Codex
**Related OKR:** Hackathon Điện Biên — weather analysis and forecasting

---

## Context

Thư mục `data/` chứa lẫn Parquet, manifest, notebook, downloader, transformation,
verify gate và unit test. Người phát triển khó phân biệt artifact có thể dùng trực
tiếp với code tạo ra artifact đó; import fallback cũng phụ thuộc vị trí chạy file.

## Decision

Tách artifact theo domain dưới `data/`, đặt code trong package `pipeline/`, phản
chiếu test dưới `tests/pipeline/`, và chạy CLI bằng `python -m pipeline.<module>`.

## Options Considered

### Option A: Giữ cấu trúc phẳng
- ✅ Không cần migration.
- ❌ Tiếp tục trộn code, test và dữ liệu.

### Option B: Package pipeline + data theo domain ← Selected
- ✅ Interface CLI thống nhất, import tuyệt đối và cây thư mục dễ đọc.
- ✅ Test phản chiếu module nên dễ tìm.
- ❌ Lệnh và đường dẫn cũ phải được cập nhật.

### Option C: Mỗi vertical slice sở hữu cả code lẫn data
- ✅ Locality cao cho từng slice.
- ❌ Dễ nhân đôi shared contracts và khó tìm toàn bộ artifact.

## Consequences

**Positive:**
- `data/` chỉ biểu diễn các nhóm artifact.
- Build, download, transform và verify trở thành các module rõ seam.
- Caller và test dùng chung package import.

**Negative / Trade-offs:**
- Lệnh trực tiếp `python data/<script>.py` không còn được hỗ trợ.
- Hai file SQLite/cache cũ đang bị notebook khóa có thể tạm còn ở root `data/`
  nhưng đã được ignore; chúng sẽ chuyển vào `legacy/` và `cache/` khi được nhả khóa.

## Implementation Plan

```text
1. Di chuyển artifact và code theo domain.
2. Đổi import sang pipeline.* và CLI sang python -m.
3. Tái tạo manifest có lineage phụ thuộc đường dẫn.
4. Verify bằng full unit suite và các live artifact gates.
```

## Links

- Related: ADR-003, ADR-005
- Task: DATA-LAYOUT-005
