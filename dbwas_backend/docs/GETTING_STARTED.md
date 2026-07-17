# Hướng dẫn Khởi chạy Dự án (Getting Started)

Tài liệu này dành cho Solo Builder / Hackathon Team để setup dự án nhanh chóng nhất.

## 1. Yêu cầu hệ thống
- Python 3.10+
- Redis (Cần thiết cho Celery Queue)
- SQLite (Đã có sẵn trong Python)

## 2. Thứ tự Build & Setup Khuyến nghị

Hãy thực hiện theo ĐÚNG thứ tự dưới đây để tránh bị rối:

- [ ] **Bước 1: Setup Môi trường**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  pip install -r requirements.txt
  ```
  *Lý do:* Cách ly môi trường, đảm bảo thư viện không xung đột.

- [ ] **Bước 2: Cấu hình biến môi trường**
  Copy file `.env.example` thành `.env` và điền các API Key (OpenAI, Zalo OA, SMS Gateway).

- [ ] **Bước 3: Chạy Redis Server**
  Trên Windows, bạn có thể dùng Memurai hoặc cài Redis qua WSL.
  *Lý do:* Redis là bắt buộc để làm Message Broker cho Celery.

- [ ] **Bước 4: Build Core & Models (app/core, app/models)**
  Tạo kết nối Database SQLite và định nghĩa schema Pydantic trước.

- [ ] **Bước 5: Build RAG & Agent (app/rag, app/agents)**
  Mô phỏng đọc JSON từ `output_model_sample.json`, RAG tìm văn bản, LLM suy nghĩ và gọi các hàm dummy.

- [ ] **Bước 6: Tích hợp Celery Workers (app/workers)**
  Kết nối Agent đẩy task vào Queue thay vì chạy thẳng.

- [ ] **Bước 7: Viết API Endpoints (app/api)**
  Gắn Router FastAPI để chọc vào Database và Agent.

- [ ] **Bước 8: Chạy thử toàn hệ thống**
  Mở 2 Terminal:
  - Terminal 1 (Chạy API): `uvicorn app.main:app --reload`
  - Terminal 2 (Chạy Worker): `celery -A app.workers.tasks worker --loglevel=info`

## 3. Gỡ lỗi (Troubleshooting)
- Nếu Worker không nhận task -> Kiểm tra kết nối Redis trong `.env`.
- Nếu Agent trả về lỗi -> Kiểm tra lại định dạng JSON đầu vào có khớp schema Pydantic không.
