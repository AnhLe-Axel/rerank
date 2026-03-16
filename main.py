import requests
from rerank import call_rerank_api, prepare_rerank_payload
from chunks import get_raw_chunks_api, extract_chunks


def main():
    question = "Giá trị cốt lõi của FPT là gì?"

    session = requests.Session()

    response = get_raw_chunks_api(session, question)
    if response is None:
        print("Không nhận được dữ liệu từ Raw Chunks API.")
        return

    raw_chunks = extract_chunks(response)
    if raw_chunks is None:
        return

    rerank_payload = prepare_rerank_payload(question, raw_chunks)

    result = call_rerank_api(
        session,
        question=rerank_payload["question"],
        passages=rerank_payload["passages"],
        top_k=rerank_payload["top_k"]
    )

    if result is not None:
        print("Kết quả Rerank:")
        print(result)
    else:
        print("Rerank API không trả về kết quả.")


if __name__ == "__main__":
    main()
