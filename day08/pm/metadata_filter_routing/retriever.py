from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from query_router import route_query


class DenseRetriever:
    def __init__(self, dataset_dir: Path):
        self.dataset_dir = dataset_dir
        self.metadata = pd.read_csv(
            dataset_dir / "metadata.csv",
            dtype=str,
        ).fillna("")

        self.documents = [
            (
                dataset_dir
                / "documents"
                / row["file_name"]
            ).read_text(encoding="utf-8")
            for _, row in self.metadata.iterrows()
        ]

        self.model = SentenceTransformer(
            "intfloat/multilingual-e5-small"
        )

        self.embeddings = self.model.encode(
            [f"passage: {text}" for text in self.documents],
            normalize_embeddings=True,
        )

    def _search(
        self,
        question: str,
        candidate_indices: list[int],
        top_k: int = 3,
    ) -> list[str]:
        query_embedding = self.model.encode(
            [f"query: {question}"],
            normalize_embeddings=True,
        )[0]

        scores = (
            self.embeddings[candidate_indices]
            @ query_embedding
        )

        top_positions = np.argsort(scores)[::-1][:top_k]

        return [
            self.metadata.iloc[
                candidate_indices[position]
            ]["document_id"]
            for position in top_positions
        ]

    def baseline_search(self, question: str) -> dict:
        start = perf_counter()
        candidates = list(range(len(self.metadata)))

        results = self._search(question, candidates)

        return {
            "documents": results,
            "latency_ms": (perf_counter() - start) * 1000,
            "search_calls": 1,
            "llm_calls": 0,
            "token_usage": 0,
        }

    def improved_search(self, question: str) -> dict:
        start = perf_counter()
        routing = route_query(question)

        if routing["categories"]:
            mask = self.metadata["category"].isin(
                routing["categories"]
            )
            candidates = self.metadata.index[mask].tolist()
        else:
            candidates = list(range(len(self.metadata)))

        # 필터 결과가 없으면 전체 검색
        if not candidates:
            candidates = list(range(len(self.metadata)))

        results = self._search(question, candidates)

        return {
            "documents": results,
            "route": routing["route"],
            "matched_keywords": routing["matched_keywords"],
            "candidate_ids": self.metadata.iloc[
                candidates
            ]["document_id"].tolist(),
            "candidate_count": len(candidates),
            "latency_ms": (perf_counter() - start) * 1000,
            "search_calls": 1,
            "llm_calls": 0,
            "token_usage": 0,
        }