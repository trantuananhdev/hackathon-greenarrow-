import os
from pydantic_ai import Agent, RunContext
from rich.console import Console
from rich.table import Table
from app.rag.policy_engine import rag_engine

console = Console()

# Cấu hình PydanticAI dùng Gemini 1.5 Flash (Nhanh, Free)
# Lưu ý: pydantic_ai tự động đọc GEMINI_API_KEY từ environment
agent = Agent(
    'gemini-1.5-flash',
    system_prompt=(
        "Bạn là trí tuệ nhân tạo điều phối cảnh báo thời tiết cực đoan của tỉnh Điện Biên. "
        "Nhiệm vụ của bạn là nhận thông tin thời tiết đầu vào và quyết định kênh phân phối phù hợp. "
        "LUÔN KIỂM TRA văn bản chỉ đạo khẩn cấp (RAG) trước khi ra quyết định. Nếu có chỉ đạo, phải TUÂN THỦ TUYỆT ĐỐI. "
        "Dùng các tool: send_sms, send_zalo, trigger_auto_call, translate_text để gửi tin nhắn. "
        "Đối với vùng dân tộc thiểu số, hãy ưu tiên dùng auto-call."
    )
)

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
