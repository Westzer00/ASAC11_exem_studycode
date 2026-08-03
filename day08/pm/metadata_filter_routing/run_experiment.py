from pathlib import Path

import pandas as pd

from evaluator import evaluate, parse_documents
from retriever import DenseRetriever


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "rag_dataset"
RESULT_DIR = BASE_DIR / "results"


def main():
    RESULT_DIR.mkdir(exist_ok=True)

    questions = pd.read_csv(
        DATASET_DIR / "questions.csv",
        dtype=str,
    )

    ground_truth = pd.read_csv(
        DATASET_DIR / "ground_truth.csv",
        dtype=str,
    )

    data = questions.merge(ground_truth, on="question_id")
    retriever = DenseRetriever(DATASET_DIR)

    rows = []

    for _, row in data.iterrows():
        question = row["question"]
        relevant = parse_documents(row["relevant_documents"])

        baseline = retriever.baseline_search(question)
        improved = retriever.improved_search(question)

        baseline_score = evaluate(
            baseline["documents"],
            relevant,
        )
        improved_score = evaluate(
            improved["documents"],
            relevant,
        )

        excluded = set(relevant) - set(
            improved["candidate_ids"]
        )

        rows.append({
            "question_id": row["question_id"],
            "question": question,
            "relevant_documents": ";".join(relevant),

            "baseline_top3": ";".join(baseline["documents"]),
            "baseline_hit": baseline_score["hit"],
            "baseline_recall": baseline_score["recall"],
            "baseline_rr": baseline_score["rr"],
            "baseline_latency_ms": baseline["latency_ms"],

            "route": improved["route"],
            "candidate_count": improved["candidate_count"],
            "improved_top3": ";".join(improved["documents"]),
            "improved_hit": improved_score["hit"],
            "improved_recall": improved_score["recall"],
            "improved_rr": improved_score["rr"],
            "improved_latency_ms": improved["latency_ms"],

            "search_calls": improved["search_calls"],
            "llm_calls": improved["llm_calls"],
            "token_usage": improved["token_usage"],

            "failure": (
                "정답 미검색"
                if improved_score["hit"] == 0
                else ""
            ),
            "side_effect": (
                f"필터가 정답 제외: {';'.join(excluded)}"
                if excluded
                else ""
            ),
        })

    results = pd.DataFrame(rows)
    results.to_csv(
        RESULT_DIR / "results.csv",
        index=False,
        encoding="utf-8-sig",
    )

    summary = pd.DataFrame([
        {
            "method": "baseline",
            "hit_rate": results["baseline_hit"].mean(),
            "recall_at_3": results["baseline_recall"].mean(),
            "mrr": results["baseline_rr"].mean(),
            "avg_latency_ms": results[
                "baseline_latency_ms"
            ].mean(),
        },
        {
            "method": "metadata_filter_routing",
            "hit_rate": results["improved_hit"].mean(),
            "recall_at_3": results["improved_recall"].mean(),
            "mrr": results["improved_rr"].mean(),
            "avg_latency_ms": results[
                "improved_latency_ms"
            ].mean(),
        },
    ])

    summary.to_csv(
        RESULT_DIR / "summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print(summary)


if __name__ == "__main__":
    main()