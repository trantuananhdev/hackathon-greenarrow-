from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load env
load_dotenv()

from app.rag.policy_engine import rag_engine
from app.agents.dispatcher import agent
from rich.console import Console

console = Console()
app = FastAPI(title="DBWAS Backend API")

# Mô hình dữ liệu đầu vào dựa trên output_model_sample.json
class PredictionItem(BaseModel):
    title: str
    probability: int

class WeatherForecast(BaseModel):
    forecast: List[PredictionItem]
    disasters: List[PredictionItem]

@app.on_event("startup")
async def startup_event():
    console.print("[bold green]Khởi động DBWAS Backend - Nạp RAG Engine...[/bold green]")
    # Thêm một văn bản giả định để test RAG
    rag_engine.add_document(
        text="CÔNG ĐIỆN KHẨN 04/CĐ: Khi có lũ quét hoặc ngập lụt, KHÔNG sử dụng Zalo, BẮT BUỘC dùng hệ thống AUTO-CALL tới Trưởng bản và phát Loa Âm thanh báo động cấp 1.",
        metadata={"id": "CD04", "expires": "2026-09-01"}
    )
    console.print("[bold green]RAG Policy Engine đã sẵn sàng.[/bold green]")

@app.post("/api/trigger-alert")
async def trigger_alert(data: WeatherForecast):
    """
    Nhận JSON dự báo thời tiết và đưa cho AI Agent xử lý.
    """
    try:
        # Lọc ra các thảm họa có xác suất > 80% để AI dễ xử lý
        urgent_disasters = [d.title for d in data.disasters if d.probability > 80]
        if not urgent_disasters:
            return {"status": "success", "message": "Không có thảm họa nghiêm trọng."}
            
        prompt = (
            f"Hệ thống vừa phát hiện các rủi ro cực kỳ cao (>80%): {', '.join(urgent_disasters)}. "
            f"Dân số mục tiêu: 100 người Kinh (cần Zalo/SMS), 50 người Thái (không biết chữ, cần Auto-call tiếng Thái), "
            f"1 Trưởng bản người Mông. Hãy ra quyết định ngay."
        )
        
        console.print(f"\n[bold magenta]=== KÍCH HOẠT AI AGENT ===[/bold magenta]")
        console.print(f"Input: {urgent_disasters}")
        
        # Chạy Agent (dùng run_sync cho API đơn giản)
        result = agent.run_sync(prompt)
        
        console.print(f"\n[bold green]=== KẾT QUẢ AI ===[/bold green]")
        console.print(result.data)
        
        return {
            "status": "success", 
            "ai_decision": result.data,
            "detected_disasters": urgent_disasters
        }
    except Exception as e:
        console.print_exception()
        raise HTTPException(status_code=500, detail=str(e))
