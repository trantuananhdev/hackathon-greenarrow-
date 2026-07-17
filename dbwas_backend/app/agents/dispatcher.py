import os
import httpx
from typing import Any

# Dummy RunContext để giữ nguyên signature các hàm tool bên dưới
class RunContext:
    pass

from rich.console import Console
from rich.table import Table
from app.rag.policy_engine import rag_engine

console = Console()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_MODEL = "gemini-2.5-flash"
SYSTEM_PROMPT = (
    "Bạn là trí tuệ nhân tạo điều phối cảnh báo thời tiết cực đoan của tỉnh Điện Biên. "
    "Nhiệm vụ của bạn là nhận thông tin thời tiết đầu vào và quyết định kênh phân phối phù hợp. "
    "LUÔN KIỂM TRA văn bản chỉ đạo khẩn cấp (RAG) trước khi ra quyết định. Nếu có chỉ đạo, phải TUÂN THỦ TUYỆT ĐỐI. "
    "Dùng các tool: send_sms, send_zalo, trigger_auto_call, translate_text để gửi tin nhắn. "
    "Đối với vùng dân tộc thiểu số, hãy ưu tiên dùng auto-call."
)

class _Result:
    """Wrapper để giữ nguyên interface result.data như cũ."""
    def __init__(self, data: str):
        self.data = data

class GeminiAgent:
    """
    Thay thế pydantic_ai.Agent bằng cách gọi HTTP API trực tiếp
    tới endpoint v1beta/interactions của Gemini.
    """
    def tool(self, func):
        """No-op decorator để giữ nguyên các @agent.tool bên dưới."""
        return func

    def run_sync(self, user_prompt: str) -> _Result:
        api_key = os.getenv("GEMINI_API_KEY")
        full_input = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        response = httpx.post(
            GEMINI_API_URL,
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "model": GEMINI_MODEL,
                "input": full_input,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        payload = response.json()
        # Trích xuất text từ response
        text = payload.get("output", "") or str(payload)
        return _Result(data=text)

agent = GeminiAgent()

@agent.tool
def query_urgent_policy(ctx: RunContext, weather_condition: str) -> str:
    """Tra cứu (RAG) các văn bản chỉ đạo khẩn cấp liên quan đến thời tiết hiện tại."""
    policy = rag_engine.check_urgent_policy(weather_condition)
    console.print(f"[bold yellow][RAG QUERY][/bold yellow] Tìm kiếm: {weather_condition} -> Kết quả: {policy[:100]}...")
    return policy

@agent.tool
def send_sms(ctx: RunContext, phone: str, message: str) -> str:
    """Sử dụng tool này để gửi tin nhắn SMS khẩn cấp."""
    table = Table(title="[MOCK] SMS GATEWAY")
    table.add_column("Phone", style="cyan")
    table.add_column("Message", style="magenta")
    table.add_column("Status", style="green")
    table.add_row(phone, message, "SUCCESS")
    console.print(table)
    return "SMS Sent"

@agent.tool
def send_zalo(ctx: RunContext, phone: str, message: str, color_level: str) -> str:
    """Sử dụng tool này để gửi tin Zalo ZNS (có màu cảnh báo: Đỏ, Cam, Vàng)."""
    table = Table(title=f"[MOCK] ZALO OA - CẤP ĐỘ {color_level}")
    table.add_column("Phone", style="cyan")
    table.add_column("Content", style="magenta")
    table.add_row(phone, message)
    console.print(table)
    return "Zalo Sent"

@agent.tool
def trigger_auto_call(ctx: RunContext, phone: str, ethnic_lang: str, alert_type: str) -> str:
    """Kích hoạt hệ thống gọi điện tự động bằng tiếng dân tộc (Thái, Mông...)."""
    table = Table(title="[MOCK] AUTO-CALL SYSTEM")
    table.add_column("Phone", style="cyan")
    table.add_column("Language", style="yellow")
    table.add_column("Siren/Alert", style="red")
    table.add_row(phone, ethnic_lang, f"Phát âm thanh {alert_type}")
    console.print(table)
    return "Call Queued"

@agent.tool
def translate_text(ctx: RunContext, text: str, target_lang: str) -> str:
    """Sử dụng tool này để dịch văn bản tiếng Kinh sang tiếng dân tộc (Thái, Mông)."""
    # Dùng LLM dịch luôn (Mock)
    console.print(f"[bold blue][TRANSLATE][/bold blue] Dịch sang {target_lang}: '{text}'")
    return f"[Bản dịch {target_lang} của '{text}']"
