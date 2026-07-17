# Kế hoạch pipeline dự báo và cảnh báo Điện Biên

## Mục tiêu hiện tại

Xây dựng vertical slice có thể demo:

```text
Forecast snapshot → tổng hợp chỉ số → đánh giá rủi ro → cảnh báo theo địa điểm
```

Việc tải ERA5 bulk không còn là điều kiện tiên quyết.

## Nguyên tắc dữ liệu

- `location_id` là khóa join xuyên suốt.
- Locations master gồm 85 điểm đại diện cho đơn vị hành chính cũ, hiện ánh xạ
  được 30/45 đơn vị mới; chưa chứa polygon ranh giới. Overview vẫn có đủ 45
  đơn vị theo Nghị quyết 1661, nhưng 15 đơn vị thiếu location được đánh dấu
  `missing_location_data`, không được coi là trạng thái bình thường.
- Forecast được lưu theo snapshot và không ghi đè.
- Khóa forecast là `location_id + snapshot_at + valid_time + model`.
- `issued_at` chỉ dùng khi biết thời điểm model được phát hành thực sự.
- Enrichment như elevation được lưu riêng khỏi locations master.
- Timestamp nghiệp vụ dùng `Asia/Ho_Chi_Minh`; phép tính lead time dùng
  timestamp timezone-aware.
- Mọi output phải có provenance, atomic write, validation và resume.

## P0 — Data contract

Tạo validator dùng chung cho:

- khóa không trùng;
- location ID hợp lệ;
- timezone;
- biến bắt buộc không rỗng hoàn toàn;
- tọa độ grid không lệch bất thường;
- số điểm và số mốc thời gian.

Phân biệt biến forecast bắt buộc và tùy chọn. Biến tùy chọn thiếu tạo warning,
không làm hỏng toàn bộ snapshot.

## P1 — Forecast và elevation

### Elevation

- Lấy elevation cho 85 điểm.
- Lưu `location_features.parquet`, không sửa locations master.
- Khóa duy nhất: `location_id`.

### Forecast

- Batch 15 điểm, tổng cộng 6 batch.
- Forecast tối đa 16 ngày.
- Lưu partition:

```text
forecast/
└── snapshot_date=YYYY-MM-DD/
    └── snapshot_time=HHMM/
        └── part-NNN.parquet
```

- Biến bắt buộc: nhiệt độ, lượng mưa, weather code, tốc độ gió.
- Biến tùy chọn: xác suất mưa và gió giật.
- Chia horizon:
  - 0–72 giờ: cảnh báo hành động;
  - 73–168 giờ: cảnh báo sớm;
  - 169–384 giờ: xu hướng.

## P2 — Alert rules MVP

Rule chạy trên dữ liệu đã aggregate, không chạy trực tiếp trên từng dòng hourly:

- mưa: rolling 24 giờ và 72 giờ;
- rét: nhiệt độ trung bình ngày;
- mưa kéo dài: tín hiệu cần theo dõi, không khẳng định dự báo sạt lở;
- gió: phân biệt tốc độ gió duy trì và gió giật.

Rule MVP dùng tốc độ gió duy trì trên 60 km/h và gió giật trên 75 km/h làm
ngưỡng sàng lọc ban đầu. Đây chưa phải cảnh báo chính thức; `rule_version` được
lưu cùng output để có thể hiệu chỉnh mà không làm mất dấu ngưỡng đã sử dụng.

Mỗi cảnh báo phải chứa:

- địa điểm và khoảng thời gian hiệu lực;
- loại rủi ro, mức độ và độ tin cậy;
- chỉ số thực tế, ngưỡng và đơn vị;
- thông điệp tiếng Việt và hành động đề xuất;
- nguồn dữ liệu và phiên bản rule.

Cảnh báo giữ chi tiết cho 85 điểm cũ. Với 30 đơn vị mới đã có location, mức rủi
ro lấy mức cao nhất trong các điểm cũ trực thuộc, không lấy trung bình. Mười lăm
đơn vị còn thiếu tọa độ có severity `unavailable`.

## Sau MVP

1. P3 — GloFAS tại các điểm nằm trên mạng lưới sông.
2. P4 — xác minh DesInventar và tải ERA5 theo cửa sổ sự kiện.
3. P5 — World Bank stations nếu xác minh được artifact trong 60 phút.
4. P6 — OWM nếu có API key và P1–P4 đã ổn định.
5. P7 — NCHMF nếu còn thời gian.

## Verify gate P0–P2

- Snapshot đủ 85 `location_id`.
- Có đủ 6 part hoặc số part tương ứng với batch được cấu hình.
- Không trùng khóa forecast.
- Timezone và lead time đúng.
- Rule dùng rolling/daily aggregation.
- Có cảnh báo theo điểm cũ và tổng hợp lên đơn vị mới.
- Cảnh báo giải thích được giá trị, ngưỡng và hành động.
- Chạy lại không sinh bản ghi trùng.
- Lỗi giữa chừng có thể resume.
- Không ghi API key vào Git, notebook hoặc log.
