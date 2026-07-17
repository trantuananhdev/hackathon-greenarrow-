# Dữ liệu thời tiết và địa danh Điện Biên

`data/reference/dien_bien_locations.parquet` lưu tọa độ điểm trung tâm của 85 đơn vị hành
chính cũ và tên đơn vị mới tương ứng sau sắp xếp tháng 7/2025.

Ánh xạ tên mới được hiệu chỉnh theo Nghị quyết
`1661/NQ-UBTVQH15` ngày 16/06/2025. Script nhập liệu sửa các lỗi cơ học đã biết
trong bảng tọa độ nguồn, gồm Mường Thán → Mường Thín và các ánh xạ của Chiềng
Đông, Ẳng Tở, Sam Mứn, Keo Lôm.

## Danh mục địa danh

Các cột trong `dien_bien_locations.parquet`:

- `location_id`: mã điểm ổn định.
- `province`: tỉnh Điện Biên.
- `old_admin_unit`: tên xã, phường hoặc thị trấn cũ.
- `new_admin_unit`: tên đơn vị hành chính mới tương ứng.
- `latitude`, `longitude`: tọa độ điểm đại diện của đơn vị cũ.
- `coordinate_reference`: mô tả ý nghĩa và độ chính xác của tọa độ.

File hiện có 85 điểm hành chính cũ nhưng chỉ phủ 30/45 đơn vị mới theo Nghị
quyết 1661/NQ-UBTVQH15. Pipeline cảnh báo không suy diễn dữ liệu cho 15 đơn vị
thiếu; các đơn vị này được đánh dấu `missing_location_data`.

## Dữ liệu lịch sử

`pipeline/download/download_historical_weather.py` tải ERA5 theo giờ cho giai đoạn
2021–2025 và ghi
`data/weather/history/year=YYYY/q=QX/part-NNN.parquet`.

- Múi giờ: `Asia/Ho_Chi_Minh` (`UTC+7`).
- Số điểm: 85.
- Số dòng dự kiến: 3.725.040.
- Model: ERA5, dùng thống nhất cho toàn bộ giai đoạn.
- Đơn vị và fingerprint cấu hình được lưu trong
  `data/weather/history/_manifest.json`.
- Mỗi request tải một quý cho tối đa 10 điểm; nghỉ mặc định 60 giây.
- Part được ghi qua file tạm, kiểm tra số giờ, khóa trùng và biến rỗng trước
  khi publish. Chạy lại lệnh sẽ kiểm tra rồi bỏ qua các part hợp lệ.

## Tạo lại danh mục địa danh

```powershell
python -m pipeline.build.build_locations_parquet <pasted-text.txt> data/reference/dien_bien_locations.parquet
```

## Tải hoặc resume lịch sử

```powershell
python -m pipeline.download.download_historical_weather
```

Nếu thư mục output còn manifest/layout cũ không tương thích, chạy một lần:

```powershell
python -m pipeline.download.download_historical_weather --reset-incompatible
```

Flag này chỉ hoạt động khi manifest xác nhận đúng dataset Điện Biên, sau đó xóa
`_manifest.json` và các file `part-*.parquet` do pipeline tạo. Các file khác,
kể cả file nằm trong partition `year=YYYY`, được giữ nguyên. Không đặt flag này
trong notebook; chỉ chạy thủ công sau khi đã xác nhận cần bỏ dataset cũ.

Kiểm tra toàn bộ dataset sau khi tải:

```powershell
python -m pipeline.verify.verify_weather_history
```

Đọc thử mà không nạp toàn bộ dataset vào RAM:

```python
import pyarrow.dataset as ds

dataset = ds.dataset(
    "data/weather/history",
    format="parquet",
    partitioning="hive",
)
preview = dataset.head(100).to_pandas()
```

## Điểm sông cho GloFAS

Điểm sông là master độc lập tại `data/reference/river_points.parquet`, dùng
`river_point_id` thay vì `location_id`. Mười hai điểm hiện tại là node thật lấy từ
ba OSM ways của Nậm Rốm, Nậm Mức và Nậm Lay; chúng không đại diện cho tâm xã và
không được dùng để suy ra trực tiếp đơn vị hành chính.
