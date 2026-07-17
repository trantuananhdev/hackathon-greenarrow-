# Dữ liệu thời tiết và địa danh Điện Biên

`data/dien_bien_locations.parquet` lưu tọa độ điểm trung tâm của 85 đơn vị hành
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

## Dữ liệu lịch sử

`data/download_historical_weather.py` tải ERA5 theo giờ cho giai đoạn
2016–2025 và ghi `data/weather_history/year=YYYY/part-NNN.parquet`.

- Múi giờ: `Asia/Ho_Chi_Minh` (`UTC+7`).
- Số điểm: 85.
- Số dòng dự kiến: 7.452.120.
- Model: ERA5, dùng thống nhất cho toàn bộ giai đoạn.
- Đơn vị và fingerprint cấu hình được lưu trong
  `data/weather_history/_manifest.json`.
- Part được ghi qua file tạm, kiểm tra số giờ, khóa trùng và biến rỗng trước
  khi publish. Chạy lại lệnh sẽ kiểm tra rồi bỏ qua các part hợp lệ.

## Tạo lại danh mục địa danh

```powershell
python data/build_locations_parquet.py <pasted-text.txt> data/dien_bien_locations.parquet
```

## Tải hoặc resume lịch sử

```powershell
python data/download_historical_weather.py
```

Kiểm tra toàn bộ dataset sau khi tải:

```powershell
python data/verify_weather_history.py
```

Đọc thử mà không nạp toàn bộ dataset vào RAM:

```python
import pyarrow.dataset as ds

dataset = ds.dataset(
    "data/weather_history",
    format="parquet",
    partitioning="hive",
)
preview = dataset.head(100).to_pandas()
```
