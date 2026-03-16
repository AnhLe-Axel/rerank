import requests


def get_raw_chunks_api(session, question: str):
    url = "https://agents.fpt.ai/console/api/webhooks/triggers/01KKKCW3T0WC2V21QYCYDHKEX8"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer ''"
    }
    payload = {
        "sys.user_message": question
    }

    try:
        response = session.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as err:
        print(f"Lỗi khi gọi Agent API: {err}")
        if hasattr(err, "response") and err.response is not None:
            print(f"Chi tiết lỗi từ server: {err.response.text}")
        return None


def extract_chunks(response: dict) -> list[dict] | None:
    """Navigate the nested API response and remap each result
    to the format expected by prepare_rerank_payload():
      { chunk_id, data: { content: {title, context} }, score }
    """
    try:
        results = (
            response["data"]["execution_data"][0]["outputs"]["results"]
        )
    except (KeyError, IndexError, TypeError) as err:
        print(f"Không thể trích xuất chunks từ response: {err}")
        return None

    chunks = []
    for r in results:
        chunks.append({
            "chunk_id": r["_id"],
            "data": {"content": r["info"]["content"]},
            "score": r.get("score", 0.0),
        })
    return chunks
