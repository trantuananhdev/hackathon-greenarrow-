from typing import List, Dict

class _Document:
    """Lưu một đoạn văn bản chỉ đạo và metadata."""
    def __init__(self, text: str, metadata: dict):
        self.page_content = text
        self.metadata = metadata

class PolicyRAGEngine:
    """
    RAG Engine đơn giản dùng keyword search trong bộ nhớ.
    Thay thế FAISS + Google Embeddings để tránh lỗi API 404.
    Interface công khai giữ nguyên: add_document() và check_urgent_policy().
    """
    def __init__(self):
        self._documents: List[_Document] = []
        print("[RAG Engine] Khởi tạo In-Memory Keyword Search Engine.")

    def add_document(self, text: str, metadata: dict = None):
        """Thêm văn bản chỉ đạo khẩn vào bộ nhớ (chunk theo dấu câu)."""
        if metadata is None:
            metadata = {}
        # Chia nhỏ thô theo 500 ký tự, overlap 50
        chunk_size = 500
        overlap = 50
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap if end < len(text) else end

        for chunk in chunks:
            self._documents.append(_Document(text=chunk, metadata=metadata))

        print(f"[RAG Engine] Đã load {len(chunks)} chunks vào In-Memory Store.")

    def check_urgent_policy(self, query: str, k: int = 2) -> str:
        """Tìm văn bản liên quan bằng keyword matching (đơn giản, không cần API)."""
        if not self._documents:
            return "Không có văn bản chỉ đạo khẩn nào trong hệ thống."

        query_words = set(query.lower().split())

        def score(doc: _Document) -> int:
            content_lower = doc.page_content.lower()
            return sum(1 for w in query_words if w in content_lower)

        ranked = sorted(self._documents, key=score, reverse=True)
        top_docs = ranked[:k]

        if not top_docs or score(top_docs[0]) == 0:
            return "Không tìm thấy quy định nào liên quan."

        context = "\n\n".join([f"Trích xuất: {d.page_content}" for d in top_docs])
        return context

# Singleton instance
rag_engine = PolicyRAGEngine()
