import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PolicyRAGEngine:
    def __init__(self):
        # Yêu cầu phải có biến môi trường GOOGLE_API_KEY hoặc GEMINI_API_KEY
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[CẢNH BÁO] Chưa cấu hình GEMINI_API_KEY. RAG sẽ không hoạt động.")
            
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=api_key
        )
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
    def add_document(self, text: str, metadata: dict = None):
        """Thêm văn bản chỉ đạo khẩn vào FAISS In-Memory"""
        if metadata is None:
            metadata = {}
        
        chunks = self.text_splitter.create_documents([text], metadatas=[metadata])
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vector_store.add_documents(chunks)
            
        print(f"[RAG Engine] Đã load {len(chunks)} chunks vào VectorDB (FAISS).")
        
    def check_urgent_policy(self, query: str, k: int = 2) -> str:
        """Kiểm tra xem có văn bản nào match với hoàn cảnh thời tiết hiện tại không"""
        if self.vector_store is None:
            return "Không có văn bản chỉ đạo khẩn nào trong hệ thống."
            
        docs = self.vector_store.similarity_search(query, k=k)
        if not docs:
            return "Không tìm thấy quy định nào liên quan."
            
        context = "\n\n".join([f"Trích xuất: {d.page_content}" for d in docs])
        return context

# Singleton instance
rag_engine = PolicyRAGEngine()
