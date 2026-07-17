# Bảng kiểm kê dữ liệu — Hệ thống dự báo & cảnh báo sớm Điện Biên

*Cập nhật: 17/07/2026 · Phân loại theo vai trò trong hệ thống · Trạng thái: ✅ dùng ngay · 🟡 một phần/chờ · 🔴 cần Ban tổ chức*

> Xem chi tiết nguồn & cách kết hợp tại [Nghien-cuu-nguon-du-lieu.md](Nghien-cuu-nguon-du-lieu.md); tham chiếu OWM 4.0 tại [OpenWeatherMap-OneCall-4.0-reference.md](OpenWeatherMap-OneCall-4.0-reference.md).

---

## A. Dữ liệu DỰ BÁO (tương lai) — "bộ não" dự báo thô

| Nguồn | Cung cấp gì | Trạng thái | Dùng cho |
|---|---|---|---|
| **Open-Meteo Forecast** | Dự báo tới 16 ngày, theo giờ: nhiệt độ, mưa, gió, độ ẩm, xác suất mưa | ✅ Chạy được ngay (không cần key) | **Nguồn dự báo chính** cho mọi địa điểm |
| **OpenWeatherMap** (4.0 khi thông, tạm 2.5) | Dự báo 5 ngày–1.5 năm, mô tả tiếng Việt sẵn | 🟡 2.5 chạy, 4.0 chờ kích hoạt | **Đối chiếu chéo** → tính độ đồng thuận/độ tin cậy |
| **Open-Meteo Flood (GloFAS)** | Lưu lượng sông mô phỏng, ~5 km, dự báo tới 7 tháng | ✅ Chạy được | **Tín hiệu phụ** cho cảnh báo lũ |

## B. Dữ liệu QUAN TRẮC THỰC (hiện tại) — để hiệu chỉnh & nowcasting

| Nguồn | Cung cấp gì | Trạng thái | Dùng cho |
|---|---|---|---|
| **Đài KTTV Điện Biên** | Số đo trạm chính thức tại chỗ | 🔴 Cần BTC (chưa có) | Hiệu chỉnh bias, cảnh báo tức thời |
| **Vrain (WATEC)** | 1.300+ trạm đo mưa tự động thời gian thực, có trạm ở Điện Biên, xuất Excel | 🟡 Xem web công khai | **Thay thế** cho dữ liệu KTTV: bias correction + nowcasting mưa |

## C. Dữ liệu LỊCH SỬ KHÍ TƯỢNG — để định ngưỡng & phân tích lệch

| Nguồn | Cung cấp gì | Trạng thái | Dùng cho |
|---|---|---|---|
| **Open-Meteo Historical (ERA5)** | Tái phân tích từ 1940, theo giờ | ✅ Chạy được | Tính **ngưỡng percentile** mưa/rét cho từng xã; phân tích bias |
| **172 trạm mưa World Bank** | Mưa ngày 1975–2006, có GPS từng trạm | ✅ Tải tự do | Kiểm chứng độ lệch ERA5 ↔ trạm thật |

## D. Dữ liệu LỊCH SỬ THIÊN TAI — để xác định vùng nguy cơ & hiệu chỉnh ngưỡng

| Nguồn | Cung cấp gì | Trạng thái | Dùng cho |
|---|---|---|---|
| **DesInventar Việt Nam** | 1989–2019, 1.470 sự kiện, đủ loại (lũ quét, sạt lở, rét hại…), cấp tỉnh, xuất Excel | ✅ Công khai | **Danh mục sự kiện** → gắn với mưa gây sự kiện để định ngưỡng |
| **EM-DAT / WB Climate Portal** | Thảm họa lớn 1900–2024 | ✅ Công khai | Bối cảnh dài hạn |
| **Báo cáo Ban Chỉ huy PCTT tỉnh** | Chi tiết đến xã, cập nhật | 🔴 Cần BTC (chưa có) | Bản đồ vùng nguy cơ chi tiết |
| **Báo chí chính thống** | Sự kiện 2020–2026 | ✅ Công khai | Bù khoảng trống sau 2019, case study |

## E. Dữ liệu ĐỊA LÝ/TĨNH — để chi tiết hóa theo xã

| Nguồn | Cung cấp gì | Trạng thái | Dùng cho |
|---|---|---|---|
| **Ranh giới hành chính Điện Biên** (GADM/OpenStreetMap) | Danh sách + tọa độ xã/huyện | ✅ Công khai (cần tải) | Định "cụm xã ưu tiên", điểm truy vấn dự báo |
| **Open-Meteo Elevation** | Cao độ từng điểm | ✅ Chạy được | Hiệu chỉnh nhiệt độ theo địa hình (−0.6°C/100m) |
| **Open-Meteo Geocoding** | Tên địa danh → tọa độ | ✅ Chạy được | Tra cứu địa điểm |

## F. Nguồn CẢNH BÁO CHÍNH THỨC

| Nguồn | Cung cấp gì | Trạng thái | Dùng cho |
|---|---|---|---|
| **Bản tin NCHMF** | Dự báo/cảnh báo chính thức dạng văn bản | ✅ Công khai | Nguồn cảnh báo chính thức (parse thủ công) |
| **OWM government alerts** (One Call 4.0) | Cảnh báo cơ quan khí tượng 180+ nước | 🟡 Chờ key + **chưa rõ có phủ VN** | Cảnh báo bổ sung (nếu phủ VN) |

---

## Dòng chảy xử lý

```
DỰ BÁO (A) ──┐
             ├─► hiệu chỉnh bằng QUAN TRẮC (B) ──► dự báo cụm xã chính xác hơn
ĐỊA LÝ (E) ──┘                                          │
                                                        ▼
LỊCH SỬ KHÍ TƯỢNG (C) + THIÊN TAI (D) ──► NGƯỠNG cảnh báo địa phương hóa
                                                        │
                                                        ▼
                                        so ngưỡng ──► CẢNH BÁO tự động
                                                        │
CẢNH BÁO CHÍNH THỨC (F) ──── đối chiếu ─────────────────┘
```

## Ba điều cần nhớ

1. **Chỉ 2 nhóm có "khoảng đỏ"** (cần BTC): dữ liệu Đài KTTV và báo cáo Ban Chỉ huy PCTT tỉnh. Cả hai đều có **phương án thay thế công khai** (Vrain, DesInventar, báo chí) → hệ thống vẫn chạy đủ để thi. Thiết kế nên có "cổng chờ" (adapter) để cắm dữ liệu KTTV khi được cấp.
2. **Phần lớn dữ liệu đến từ Open-Meteo** (forecast + flood + historical + elevation + geocoding) — một nguồn, miễn phí, không cần key. Đây là xương sống.
3. **Không có nguồn nào để "train model dự báo"** — dữ liệu lịch sử dùng để **định ngưỡng và hiệu chỉnh (bias correction)**, không phải để tự dự báo thời tiết. AI của đội nằm ở lớp hiệu chỉnh cục bộ + phân loại rủi ro + sinh cảnh báo đa ngôn ngữ.

## Ưu tiên thu thập (thứ tự khởi động)

| Ưu tiên | Việc | Vì sao |
|---|---|---|
| 1 | Tải ranh giới + tọa độ xã Điện Biên (GADM/OSM) | Cần trước để định điểm truy vấn |
| 2 | Kết nối Open-Meteo Forecast + Elevation cho các điểm xã | Xương sống, chạy ngay |
| 3 | Tải DesInventar (Excel) + 172 trạm WB | Định ngưỡng, không chờ ai |
| 4 | Truy ERA5 cho ngày sự kiện lịch sử | Ghép với DesInventar để hiệu chỉnh ngưỡng |
| 5 | Kết nối OWM (2.5 ngay, 4.0 khi key thông) | Đối chiếu + alerts |
| 6 | Khảo sát trạm Vrain tại Điện Biên | Nguồn quan trắc thay thế |
| 7 | Hỏi BTC dữ liệu KTTV + báo cáo PCTT | Cần thời gian, xin song song |
