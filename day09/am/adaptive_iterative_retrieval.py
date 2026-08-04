from pathlib import Path
from time import perf_counter
import re #정규식 추출

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# 경로
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[1]
DATA_DIR = ROOT_DIR / "day08" / "pm" / "rag_dataset"
RESULT_DIR = BASE_DIR / "results"

# 기준값
TOP_K = 3
MIN_VALID_SCORE = 0.55
MIN_GOOD_SCORE = 0.75


# 데이터 로딩
metadata = pd.read_csv(
    DATA_DIR / "metadata.csv",
    dtype=str,
    ).fillna("")

documents = [
    (
        DATA_DIR / "documents"/ row["file_name"]
    ).read_text(encoding="utf-8")
    for _, row in metadata.iterrows()
]

# 임베딩 모델 설정
model = SentenceTransformer(
    "intfloat/multilingual-e5-small"
)

# 문서를 미리 벡터로 변환한뒤 실행 할꺼여서 1! 
document_vectors = model.encode(
    [f"passage: {text}" for text in documents],
    normalize_embeddings=True, # 모든 벡터의 길이를 1로 맞춰줌 ! 
)

# Dense retrieval 함수
def search(queries):
    if isinstance(queries, str): # 입력이 문자열 하나라면 리스트로 변환
        queries = [queries]

    query_vectors = model.encode(
        [f"query: {query}" for query in queries],
        normalize_embeddings=True,
    )

    # Multi-query인 경우 Query별 점수 중 최고값 사용 !! <- 위에를 거쳤기 때문에 멀티면 2개의 쿼리로 나옴
    scores = (
        document_vectors @ query_vectors.T
    ).max(axis=1)

    top_indices = np.argsort(scores)[::-1][:TOP_K] # top-k개 인덱스 추출

    return [
            {
                "document_id": metadata.iloc[index]["document_id"],
                "score": float(scores[index]),
                "text": documents[index],
            }
            for index in top_indices
        ] 

# 결과가 0개 일때 Query Rewrite
# 있을법한 표현으로 질문 쿼리 리라이팅
# LLM 쿼리 리라이팅 X , 사전에 정한 규칙 기반 Rewrite!!! 
def rewrite_query(question):
    rules = {
    "집에서": "재택근무 VPN",
    "돈 처리": "비용 정산 영수증",
    "쉬는 날": "연차 휴가",
    "코드 올리기": "GitLab Merge Request",
    } 

    for old, new in rules.items():
        question = question.replace(old, new)

    return question + " 공식 규정"

# 충돌방지
def has_conflict(question, results):
    patterns = {
        "비밀번호": r"비밀번호.{0,50}?(\d+)\s*일",
        "출장": r"출장.{0,100}?(\d+)\s*일",
        "연차": r"연차.{0,80}?(\d+)\s*일",
        "재택": r"재택근무.{0,80}?주\s*(\d+)\s*회",
    }

    for keyword, pattern in patterns.items():
        if keyword not in question:
            continue

        values = {
            match.group(1)
            for result in results
            if (
                match := re.search(
                    pattern,
                    result["text"],
                    re.DOTALL,
                )
            )
        }

        return len(values) >= 2 # 값이 2종류 이상이면 충돌로 판단

    return False


# Adaptive·Iterative 검색 정책
def adaptive_search(question): # 1차 겁색을 하고 결과 상태에 따라 재검색 방식 결정 !! 
    start = perf_counter()

    first_results = search(question)
    best_score = first_results[0]["score"] # 가장 유사한 1번째 문서 추출 & 점수 저장

    retry_reason = "none"
    retry_queries = []

    # 유효 결과 0개 == dense로 하면 무조건 나오니까 기준 줘서 그거 넘지 못하면 유효결과 0개
    if best_score < MIN_VALID_SCORE: 
        retry_reason = "zero_result"
        retry_queries = [rewrite_query(question)] # 재검색 Query

    # 검색 문서 충돌 == 위에 숫자 뽑은개 2개 이상인경우 충돌이라고 가정했었음
    elif has_conflict(question, first_results):
        retry_reason = "conflict"
        retry_queries = [
            question + " 최신 공식 규정",
            question + " 정책 문서",
        ]

    # 최고 점수가 낮음
    elif best_score < MIN_GOOD_SCORE:
        retry_reason = "low_score"
        retry_queries = [
            rewrite_query(question),
            question + " 관련 절차 기준",
        ]

    # 최대 2라운드 ( 1차검색 + 필요할때 2차 검색까지만 제한)
    final_results = (
        search(retry_queries)
        if retry_queries
        else first_results
    )

    success = (
        final_results[0]["score"]
        >= MIN_VALID_SCORE
    ) # 0.55이상이면 근거 찾음, 아니면 근거가 부족

    return {
        "documents": ";".join(
            result["document_id"]
            for result in final_results
        ) if success else "",
        "best_score": final_results[0]["score"],
        "retry_reason": retry_reason,
        "retry_queries": ";".join(retry_queries),
        "search_rounds": 2 if retry_queries else 1,
        "search_calls": (
            1 + len(retry_queries)
            if retry_queries
            else 1
        ),
        "status": (
            "success"
            if success
            else "insufficient_evidence"
        ),
        "user_response": (
            "근거 문서를 찾았습니다."
            if success
            else "관련 문서에서 충분한 근거를 찾지 못했습니다."
        ),
        "latency_ms": (
            perf_counter() - start
        ) * 1000,
    }


def main():
    RESULT_DIR.mkdir(exist_ok=True)

    questions = pd.read_csv(
        DATA_DIR / "questions.csv",
        dtype=str,
    )

    rows = []

    for _, row in questions.iterrows():
        result = adaptive_search(row["question"])

        rows.append({
            "question_id": row["question_id"],
            "question": row["question"],
            **result,
        })

    pd.DataFrame(rows).to_csv(
        RESULT_DIR / "results.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("완료:", RESULT_DIR / "results.csv")


if __name__ == "__main__":
    main()