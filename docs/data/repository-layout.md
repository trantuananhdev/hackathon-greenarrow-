# Bố cục data pipeline

Code và dữ liệu được tách thành các cây độc lập:

```text
data/
├── reference/       # tọa độ hành chính và điểm sông
├── features/        # đặc trưng tĩnh theo địa điểm
├── weather/         # forecast, alert và lịch sử theo giờ
├── hydrology/       # GloFAS và flood signals
├── events/          # inventory, context locations và event weather
├── cache/           # cache cục bộ, không commit
└── legacy/          # SQLite đã bị Parquet thay thế

pipeline/
├── build/           # tạo master/reference dataset
├── download/        # adapter tải nguồn bên ngoài
├── transform/       # sinh risk, alert và derived signals
├── verify/          # verify gate có thể chạy độc lập
└── shared/          # contract, parser và domain mapping dùng chung

tests/pipeline/       # phản chiếu cùng phân cấp với pipeline/
notebooks/           # notebook khám phá và trình diễn
```

Chạy module từ project root bằng `python -m`, ví dụ:

```powershell
python -m pipeline.download.download_forecast
python -m pipeline.transform.alert_rules
python -m pipeline.verify.verify_weather_alert_mvp
```

Cách gọi này giữ một interface CLI ổn định và giúp import luôn được resolve từ
package `pipeline`, không phụ thuộc thư mục hiện hành của từng script.
