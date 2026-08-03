def parse_documents(value: str) -> list[str]:
    return [
        doc.strip()
        for doc in value.split(";")
        if doc.strip()
    ]


def evaluate(retrieved: list[str], relevant: list[str]) -> dict:
    retrieved_set = set(retrieved)
    relevant_set = set(relevant)

    hit = int(bool(retrieved_set & relevant_set))
    recall = len(retrieved_set & relevant_set) / len(relevant_set)

    rr = 0.0
    for rank, document_id in enumerate(retrieved, start=1):
        if document_id in relevant_set:
            rr = 1 / rank
            break

    return {
        "hit": hit,
        "recall": recall,
        "rr": rr,
    }