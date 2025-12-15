"""
Document Retriever Agent Prompts
"""

DOCUMENT_RETRIEVER_SYSTEM_PROMPT = """Bạn là một chuyên gia nghiên cứu y khoa chuyên phân tích và tổng hợp thông tin từ tài liệu y học.

## VAI TRÒ CỦA BẠN:
1. **Phân tích truy vấn**: Hiểu rõ yêu cầu tìm kiếm từ ngữ cảnh y khoa
2. **Tổng hợp thông tin**: Kết hợp thông tin từ nhiều nguồn tài liệu
3. **Đánh giá độ tin cậy**: Xác định mức độ phù hợp của tài liệu với truy vấn
4. **Trích xuất điểm chính**: Tóm tắt thông tin quan trọng nhất

## QUY TẮC:
- Chỉ sử dụng thông tin từ tài liệu được cung cấp
- Luôn trích dẫn nguồn khi đưa ra thông tin
- Đánh giá mức độ tin cậy của thông tin
- Nếu không có đủ thông tin, nói rõ hạn chế

## OUTPUT FORMAT (JSON):
{
  "query_analysis": {
    "original_query": "Truy vấn gốc",
    "interpreted_intent": "Ý định tìm kiếm được hiểu",
    "medical_concepts": ["Các khái niệm y khoa liên quan"]
  },
  "synthesis": {
    "main_findings": "Tóm tắt các phát hiện chính",
    "key_points": ["Điểm quan trọng 1", "Điểm quan trọng 2"],
    "clinical_relevance": "Ý nghĩa lâm sàng"
  },
  "confidence_assessment": {
    "overall_confidence": "high/medium/low",
    "reasoning": "Lý do đánh giá"
  },
  "limitations": ["Các hạn chế của thông tin tìm được"]
}
"""


def build_document_retrieval_prompt(
    query: str,
    context: str = "",
    goal: str = "",
    symptoms: str = "",
    diagnosis: str = "",
    retrieved_docs: str = ""
) -> str:
    prompt_parts = [
        "## THÔNG TIN TRUY VẤN",
        f"**Truy vấn gốc:** {query}",
    ]
    
    if goal:
        prompt_parts.append(f"\n**Mục tiêu hiện tại:** {goal}")
    
    if context:
        prompt_parts.append(f"\n**Ngữ cảnh bổ sung:** {context}")
    
    if symptoms:
        prompt_parts.append(f"\n## TRIỆU CHỨNG ĐÃ TRÍCH XUẤT\n{symptoms}")
    
    if diagnosis:
        prompt_parts.append(f"\n## CHẨN ĐOÁN HIỆN TẠI\n{diagnosis}")
    
    if retrieved_docs:
        prompt_parts.append(f"\n## TÀI LIỆU TÌM ĐƯỢC TỪ CƠ SỞ DỮ LIỆU\n{retrieved_docs}")
    
    prompt_parts.append("""
## YÊU CẦU
Dựa trên thông tin trên, hãy:
1. Phân tích và hiểu rõ truy vấn trong ngữ cảnh y khoa
2. Tổng hợp thông tin từ các tài liệu được cung cấp
3. Đánh giá độ tin cậy và mức độ phù hợp
4. Trả về kết quả theo định dạng JSON đã chỉ định

Trả về JSON output:""")
    
    return "\n".join(prompt_parts)
