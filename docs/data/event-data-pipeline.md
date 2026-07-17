# P4 — DesInventar và ERA5 event windows

## Nguồn sự kiện

- Trang tải chính thức:
  <https://www.desinventar.net/DesInventar/download_base.jsp?countrycode=vnm>
- Artifact:
  <https://www.desinventar.net/DesInventar/download/DI_export_vnm.zip>
- SHA-256 đã khóa:
  `8bbfb7d0dc4443e08962fa167aa34335d0b9722c2627821825dd2a0460cdd200`
- Kích thước tại thời điểm lấy: 3.123.710 byte.

Giấy phép phần mềm DesInventar không tự động áp dụng cho dữ liệu. Dataset vẫn thuộc
đơn vị đóng góp; khi sử dụng phải ghi nguồn DesInventar/UNDRR và nguồn gốc `CCFSC`
được lưu trong datacard.

## Kết quả cho Điện Biên

Artifact Việt Nam có 1.470 datacard, trong đó chỉ có 7 bản ghi Điện Biên:

- 4 sự kiện lũ;
- 1 sự kiện lũ quét;
- 2 sự kiện lốc kèm mưa đá;
- thời gian từ 01/07/2001 đến 22/08/2008.

Tất cả chỉ có độ chính xác cấp tỉnh, không có huyện/xã và tọa độ đều bằng 0. Vì vậy
chúng là weak labels cấp tỉnh, không phải 7 × 85 nhãn dương cấp địa điểm.

Ba trường `fechano/fechames/fechadia` có đủ chữ số nhưng mô tả nguồn cho thấy nhiều
giá trị ngày/tháng chỉ là mặc định: ví dụ `01/01/2007` đi cùng mô tả “năm 2007”.
Vì vậy cả 7 bản ghi hiện mang `date_precision=unverified_day` và
`record_eligible_for_era5=false`. Không dùng `fechafec`, vì trường này là
`2010-06-11` cho cả bảy bản ghi và không phải ngày xảy ra sự kiện.

Đối chiếu báo chí lịch sử cũng cho thấy component date không đáng dùng làm ngày
chính xác: datacard lũ quét năm 2004 ghi `01/05`, trong khi sự kiện một người chết
tại Mường Phăng được tường thuật xảy ra sáng `06/07/2004`; datacard lốc/mưa đá ghi
`01/01/2004`, trong khi báo cáo khí tượng được đăng đầu tháng 4. Tham khảo:
[VnExpress 07/07/2004](https://vnexpress.net/tin-van-ngay-7-7-2005501.html) và
[Nhân Dân 06/04/2004](https://nhandan.vn/ket-thuc-thoi-ky-kho-han-keo-dai-post465307.html).

## Event weather context

Mỗi sự kiện dùng cửa sổ:

```text
event day 00:00 Asia/Ho_Chi_Minh
├── 72 giờ trước: được phép làm feature
└── 48 giờ từ thời điểm sự kiện: chỉ dùng chẩn đoán, không làm predictor
```

Để tránh quota và tránh giả vờ có nhãn cấp xã, pipeline chọn 12 điểm đại diện không
gian từ locations master bằng deterministic farthest-point sampling. Các điểm này
chỉ mô tả weather context cấp tỉnh.

Downloader chỉ nhận event có `record_eligible_for_era5=true`. Cần xác minh ngày bằng
báo cáo gốc hoặc nguồn độc lập trước khi chạy. Lần thử trước khi phát hiện vấn đề
date precision cũng gặp HTTP 429; không có weather part nào được coi là hoàn chỉnh.

Sau khi ngày đã được xác minh và inventory được cập nhật có provenance, chạy:

```powershell
python -m pipeline.download.download_event_weather `
  --events data/events/desinventar_events.parquet `
  --locations data/events/event_locations.parquet `
  --output data/events/weather `
  --batch-size 6 `
  --request-delay 60
```

Verify inventory hiện tại:

```powershell
python -m pipeline.verify.verify_event_data --allow-incomplete-weather
```

Verify đầy đủ sau khi có ít nhất một event đủ điều kiện và tải xong:

```powershell
python -m pipeline.verify.verify_event_data
```
