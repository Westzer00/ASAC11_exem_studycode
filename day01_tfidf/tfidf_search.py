import math
import re
from collections import Counter
from pathlib import Path


documents = [
    "비밀번호 변경 방법은 설정 메뉴의 보안 항목에서 확인할 수 있습니다.",
    "로그인 오류가 발생하면 비밀번호 재설정을 시도하세요.",
    "배송 조회는 주문 내역 페이지에서 확인할 수 있습니다.",
    "환불 신청은 결제 완료 후 7일 이내에 가능합니다.",
    "회원 탈퇴는 마이페이지의 계정 관리에서 진행할 수 있습니다.",
    "계좌 등록은 결제 수단 관리 메뉴에서 할 수 있습니다.",
    "계좌 해지는 고객센터 상담 후 처리됩니다.",
    "쿠폰은 결제 화면에서 적용할 수 있습니다.",
    "상품 리뷰는 배송 완료 후 작성할 수 있습니다.",
    "알림 설정은 앱 설정 메뉴에서 변경할 수 있습니다.",
]

queries = [
    ("키워드가 정확히 포함된 질문", "비밀번호 변경 방법"),
    ("의미는 같지만 표현이 다른 질문", "암호를 바꾸는 법"),
    ("단어는 비슷하지만 의미가 다른 질문", "계좌 개설 방법"),
]


def tokenize(text):
    return re.findall(r"[가-힣a-zA-Z0-9]+", text.lower())


def calculate_tf(tokens):
    counts = Counter(tokens)
    total = len(tokens)

    return {
        word: count / total
        for word, count in counts.items()
    }


def calculate_idf(documents_tokens):
    document_count = len(documents_tokens)
    all_words = set()

    for tokens in documents_tokens:
        all_words.update(tokens)

    idf = {}

    for word in all_words:
        word_document_count = 0

        for tokens in documents_tokens:
            if word in tokens:
                word_document_count += 1

        idf[word] = math.log((document_count + 1) / (word_document_count + 1)) + 1

    return idf


def make_tfidf_vector(tokens, idf):
    tf = calculate_tf(tokens)
    vector = {}

    for word, tf_score in tf.items():
        vector[word] = tf_score * idf.get(word, 0)

    return vector


def cosine_similarity(vector_a, vector_b):
    common_words = set(vector_a.keys()) & set(vector_b.keys())

    dot_product = sum(vector_a[word] * vector_b[word] for word in common_words)

    norm_a = math.sqrt(sum(score ** 2 for score in vector_a.values()))
    norm_b = math.sqrt(sum(score ** 2 for score in vector_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0

    return dot_product / (norm_a * norm_b)


def search(query, document_vectors, idf):
    query_tokens = tokenize(query)
    query_vector = make_tfidf_vector(query_tokens, idf)

    results = []

    for index, document_vector in enumerate(document_vectors):
        score = cosine_similarity(query_vector, document_vector)
        results.append((index, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:3]


def main():
    documents_tokens = [tokenize(document) for document in documents]
    idf = calculate_idf(documents_tokens)

    document_vectors = [
        make_tfidf_vector(tokens, idf)
        for tokens in documents_tokens
    ]

    report_lines = []
    report_lines.append("# TF-IDF 검색기 실습 결과\n")
    report_lines.append("## 문서 목록\n")

    for index, document in enumerate(documents, start=1):
        report_lines.append(f"{index}. {document}")

    report_lines.append("\n## 비교 질문별 검색 결과\n")

    for query_type, query in queries:
        report_lines.append(f"### {query_type}")
        report_lines.append(f"질문: `{query}`\n")

        results = search(query, document_vectors, idf)

        for rank, (document_index, score) in enumerate(results, start=1):
            report_lines.append(
                f"{rank}. 점수 {score:.4f} - {documents[document_index]}"
            )

        report_lines.append("")

    report_lines.append("## 결과 해석\n")
    report_lines.append("- 키워드가 정확히 포함된 질문은 관련 문서를 잘 찾는다.")
    report_lines.append("- 의미는 같지만 표현이 다르면 TF-IDF가 잘 찾지 못할 수 있다.")
    report_lines.append("- 단어가 비슷해도 의미가 다르면 잘못된 문서가 상위에 나올 수 있다.")
    report_lines.append("- 따라서 TF-IDF는 정확한 단어 매칭에는 강하지만 의미 이해에는 약하다.")

    result_path = Path(__file__).with_name("results.md")
    result_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("검색 결과를 results.md 파일로 저장했습니다.")


if __name__ == "__main__":
    main()