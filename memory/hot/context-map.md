# Context Map — Always Up To Date

> **AI updates this after every significant action.**
> Future sessions start by reading this file to know exactly where things stand.

---

## 🗺️ Project Position
- **Phase:** ideation (template) — hackathon pipeline ready + continuous execute
- **Sprint:** S1 — not_started
- **Focus Area:** Weather analysis — dữ liệu địa danh và Open-Meteo cho Điện Biên

## 📍 Current Position
- **Active Task:** WEATHER-HISTORY-001
- **Active Agent:** —
- **Branch:** (local)
- **File Being Modified:** data/download_historical_weather.py · data/setup_data.ipynb

## 🔗 Context Chain (read bottom-up for full picture)
1. **Mission:** AI-first autonomous development + hackathon 48h ops
2. **Quarter OKR:** (fill after onboarding product)
3. **Sprint Goal:** (fill)
4. **Current Task:** —
5. **Current Step:** Code tải ERA5 2021-2025 theo quý đã qua test/dry-run; chờ quota mới để tải và verify đủ 180 part

## ⚠️ Must Remember
- Master guide: `docs/onboarding/HUONG-DAN-SU-DUNG.md`
- Phòng IT: Đề bài → BA → CTO → Tech Lead → DEV (Enter + Review)
- Phase 7: paste Prompt **một lần** → `/done` → **auto-next** đến TRACK COMPLETE
- SSOT prompts: `WORKFLOW.md`
- Living maps: `docs/design/REPO-INDEX.md` + `BE/FE/AI-INDEX.md`
- Core: `architecture.md` · Conventions: `architecture/PROJECT.md` (phải điền thật)

## 📋 Recent Decisions (last 5)
| When | Decision | By | Reference |
|------|----------|----|-----------|
| 2026-07-17 | Scope hackathon giảm còn 2021-2025, phân vùng quý, bỏ wind_gusts_10m | human | ADR-004 |
| 2026-07-17 | Dữ liệu lịch sử dùng ERA5 + Parquet fact chỉ giữ location_id | human+ai | ADR-003 |
| 2026-07-17 | Chuẩn hóa thời gian dự báo sang Asia/Ho_Chi_Minh (UTC+7) | human+ai | data/setup_data.ipynb |
| 2026-07-17 | Ánh xạ đơn vị mới phải theo NQ 1661, không theo các đính chính thứ cấp mâu thuẫn | ai | data/build_locations_db.py |
| 2026-07-17 | Lưu tọa độ địa danh Điện Biên trong SQLite; notebook không hard-code | human+ai | data/dien_bien_locations.db |
| 2026-07-17 | Phase 7 auto-next sau /done | human+ai | WORKFLOW.md |
| 2026-07-17 | Master guide HUONG-DAN-SU-DUNG | human+ai | docs/onboarding/ |
| 2026-07-17 | Unify hackathon to 7-phase WORKFLOW SSOT | human+ai | WORKFLOW.md |

## 🔀 Recent Context Switches
| When | From | To | Reason |
|------|------|----|--------|
| 2026-07-17 | Danh sách 12 điểm hard-code | SQLite gồm 85 đơn vị cũ | Giữ chi tiết không gian và ánh xạ tên mới–cũ |
| 2026-07-17 | Review hệ thống | Master guide + auto-next | Đảm bảo Enter → hoàn thành |
| 2026-07-17 | 3-stage skill vs 6-phase WORKFLOW | single 7-phase WORKFLOW | đồng nhất thi 48h |
