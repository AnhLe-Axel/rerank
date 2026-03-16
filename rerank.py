from utils import concat_chunk, common_preprocess, normalize
import requests


def call_rerank_api(session, question: str, passages: list, top_k: int = 5):
    url = "https://ke-portal-dev.fpt.ai/information-retrieval/api/v1/rerank"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer Amx3mY92FI1BIytdnGdA83BGqt6USGpk"
    }
    payload = {
        "question": question,
        "top_k": top_k,
        "passages": passages
    }

    try:
        # Sử dụng session được truyền vào để tối ưu kết nối mạng (connection pooling)
        response = session.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()  # Tự động ném lỗi nếu status code không phải 2xx
        return response.json()

    except requests.exceptions.RequestException as err:
        print(f"Lỗi khi gọi API Rerank: {err}")
        if hasattr(err, "response") and err.response is not None:
            print(f"Chi tiết lỗi từ server: {err.response.text}")
        return None


def prepare_rerank_payload(question: str, raw_chunks: list[dict], top_k: int = 5) -> dict:
    passages = []

    for chunk in raw_chunks:
        data = chunk.get("data", {})
        content = data.get("content", {})

        # 1. Làm sạch text bằng utils.py
        merged_text = concat_chunk({"content": content})
        table_cleaned_text = common_preprocess(merged_text)
        final_clean_text = normalize(table_cleaned_text)

        # 2. Xây dựng Passage tối giản (Vứt bỏ toàn bộ metadata, upload_date, file_id...)
        passage = {
            "_id": chunk.get("chunk_id"),
            "info": {
                "content": {
                    "title": content.get("title", ""),  # Có thể gửi title gốc nếu API tự nối
                    "context": final_clean_text  # Đã được gộp và làm sạch
                }
            },
            # Giữ lại điểm ban đầu của vector search (nếu Rerank API có thuật toán mix score)
            "score": chunk.get("score", 0.0)
        }
        passages.append(passage)

    return {
        "question": question,
        "top_k": top_k,
        "passages": passages
    }