import csv
import json
import re


# ==================================================
# 1. document.json 문서 불러오기
# ==================================================

with open("document.json", encoding="utf-8") as f:
    data = json.load(f)

documents = data["documents"]
doc_map = {doc["id"]: doc for doc in documents}


# ==================================================
# 2. 평가 질문
#
# need   : 정답에 필요한 Chunk
# gold   : 정답에 포함되어야 하는 값
# answer : 실제 모델 답변
# cite   : 모델이 인용한 Chunk
# ==================================================

def Q(
    id, question_type, question, need, gold,
    answer, cite=(), fmt=None, top_k=3, relevant=None
):
    return {
        "id": id,
        "type": question_type,
        "question": question,
        "need": need,
        "gold": gold,
        "answer": answer,
        "cite": list(cite),
        "format": fmt,
        "top_k": top_k,
        "relevant": relevant or need
    }


questions = [

    # ==============================================
    # 문서에 답이 명확히 존재: 4개
    # ==============================================

    Q(
        "Q01", "문서에 답이 명확히 존재",
        "NovaAir 보증기간은?",
        ["C01"], ["3년"],
        "3년입니다.", ["C01"]
    ),

    Q(
        "Q02", "문서에 답이 명확히 존재",
        "microSD 최대 용량은?",
        ["C02"], ["512GB"],
        "512GB입니다.", ["C02"]
    ),

    Q(
        "Q03", "문서에 답이 명확히 존재",
        "고객센터의 평일 운영시간은?",
        ["C03"], ["9시", "18시"],
        "평일 9시부터 18시까지입니다.", ["C03"]
    ),

    Q(
        "Q04", "문서에 답이 명확히 존재",
        "환불 기간을 JSON으로 답하라.",
        ["C04"], ["14일"],
        "14일 이내입니다.", ["C04"],
        fmt="json"
    ),


    # ==============================================
    # 여러 Chunk를 봐야 함: 4개
    # ==============================================

    Q(
        "Q05", "여러 Chunk를 봐야 함",
        "2024년 대비 2025년 매출 증가율은?",
        ["C05", "C06"], ["25%"],
        "25% 증가했습니다.", ["C05", "C06"]
    ),

    Q(
        "Q06", "여러 Chunk를 봐야 함",
        "NovaAir Pro 본체와 배터리 합계 무게는?",
        ["C07", "C08"], ["2.7kg"],
        "2.7kg입니다.", ["C07", "C08"]
    ),

    Q(
        "Q07", "여러 Chunk를 봐야 함",
        "2024년과 2025년 매출 차이는?",
        ["C05", "C06"], ["20억"],
        "20억 원입니다.", ["C05", "C06"],
        top_k=4
    ),

    Q(
        "Q08", "여러 Chunk를 봐야 함",
        "본체는 배터리보다 몇 kg 무거운가?",
        ["C07", "C08"], ["2.1kg"],
        "본체 무게는 2.4kg입니다.", ["C07"],
        top_k=1
    ),


    # ==============================================
    # 문서와 표현이 다름: 4개
    # ==============================================

    Q(
        "Q09", "문서와 표현이 다름",
        "초기 불량 제품은 언제까지 새 제품으로 바꿀 수 있나?",
        ["C09"], ["30일"],
        "30일 이내입니다.", ["C09"]
    ),

    Q(
        "Q10", "문서와 표현이 다름",
        "한 번 충전하면 얼마나 오래 버티나?",
        ["C10"], ["8시간"],
        "최대 8시간입니다.", ["C10"]
    ),

    Q(
        "Q11", "문서와 표현이 다름",
        "밤에 조용히 사용할 때 소음은?",
        ["C11"], ["22dB"],
        "22dB입니다.", ["C11"]
    ),

    Q(
        "Q12", "문서와 표현이 다름",
        "마음이 바뀌면 며칠 안에 교환해야 하나?",
        ["C12"], ["7일"],
        "수령 후 7일 이내입니다.", ["C12"]
    ),


    # ==============================================
    # 숫자·날짜 포함: 4개
    # ==============================================

    Q(
        "Q13", "숫자·날짜 포함",
        "Legacy Cloud 종료일은?",
        ["C13"], ["2026년 12월 31일"],
        "2026년 11월 30일입니다.", ["C13"]
    ),

    Q(
        "Q14", "숫자·날짜 포함",
        "펌웨어 2.4.0 배포일은?",
        ["C14"], ["2026년 3월 15일"],
        "2026년 3월 15일입니다.", ["C15"]
    ),

    Q(
        "Q15", "숫자·날짜 포함",
        "펌웨어 2.3.5 배포일은?",
        ["C15"], ["2025년 11월 30일"],
        "2025년 11월 30일입니다.", ["C15"]
    ),

    Q(
        "Q16", "숫자·날짜 포함",
        "Premium Care 시작일은?",
        ["C16"], ["2026년 7월 1일"],
        "2026년 7월 1일입니다.", ["C16"]
    ),


    # ==============================================
    # 답이 문서에 없음: 4개
    # ==============================================

    Q(
        "Q17", "답이 문서에 없음",
        "A회사의 2027년 예상 매출은?",
        [], [],
        "150억 원입니다.", ["C18"],
        relevant=["C17", "C18"]
    ),

    Q(
        "Q18", "답이 문서에 없음",
        "A회사의 대표이사는 누구인가?",
        [], [],
        "문서에서 확인할 수 없습니다.", [],
        relevant=["C17", "C18"]
    ),

    Q(
        "Q19", "답이 문서에 없음",
        "NovaAir는 어떤 색상으로 출시되는가?",
        [], [],
        "문서에서 확인할 수 없습니다.", [],
        relevant=["C19"]
    ),

    Q(
        "Q20", "답이 문서에 없음",
        "2028년 HomeCare 구독료는?",
        [], [],
        "문서에서 확인할 수 없습니다.", [],
        relevant=["C20"]
    ),


    # ==============================================
    # 비슷한 문서가 여러 개 존재: 4개
    # ==============================================

    Q(
        "Q21", "비슷한 문서가 여러 개 존재",
        "NovaAir 보증기간은?",
        ["C21"], ["3년"],
        "3년입니다.", ["C21"]
    ),

    Q(
        "Q22", "비슷한 문서가 여러 개 존재",
        "NovaAir Pro 보증기간은?",
        ["C22"], ["5년"],
        "3년입니다.", ["C21"]
    ),

    Q(
        "Q23", "비슷한 문서가 여러 개 존재",
        "EcoClean 사용 면적은?",
        ["C23"], ["40제곱미터"],
        "40제곱미터입니다.", ["C23"]
    ),

    Q(
        "Q24", "비슷한 문서가 여러 개 존재",
        "EcoClean Plus 사용 면적은?",
        ["C24"], ["60제곱미터"],
        "60제곱미터입니다.", ["C24"]
    )
]


# ==================================================
# 3. 검색 전 질문 표현 보정
# ==================================================

aliases = {
    "초기 불량": "정상 작동하지 않는",
    "새 제품으로 바꿀": "교환",
    "한 번 충전": "완전 충전",
    "오래 버티": "작동",
    "밤에 조용히": "수면 모드 소음",
    "마음이 바뀌": "단순 변심",
    "환불 기간": "미사용 서비스 환불"
}


def expand(text):
    for before, after in aliases.items():
        text = text.replace(before, after)
    return text


# ==================================================
# 4. 간단한 문서 검색
# ==================================================

def tokens(text):
    return set(re.findall(r"[0-9A-Za-z가-힣.]+", text.lower()))


def grams(text):
    text = re.sub(r"\s+", "", text.lower())
    return {
        text[i:i + 2]
        for i in range(len(text) - 1)
    }


def similarity(question, document):
    question = expand(question)

    q_tokens = tokens(question)
    d_tokens = tokens(document)

    q_grams = grams(question)
    d_grams = grams(document)

    word_score = len(q_tokens & d_tokens)

    gram_score = (
        len(q_grams & d_grams)
        / max(1, len(q_grams | d_grams))
    )

    return word_score * 3 + gram_score


def search(item):
    ranked = sorted(
        documents,
        key=lambda doc: similarity(
            item["question"],
            doc["text"]
        ),
        reverse=True
    )

    return [
        doc["id"]
        for doc in ranked[:item["top_k"]]
    ]


# ==================================================
# 5. 평가 함수
# ==================================================

def normalize(text):
    return re.sub(r"\s+", "", text.lower())


def evaluate(item):
    retrieved = search(item)

    retrieved_set = set(retrieved)
    need = set(item["need"])
    relevant = set(item["relevant"])

    answer = normalize(item["answer"])

    # 검색 문서 관련성
    context_relevance = (
        len(relevant & retrieved_set) / len(retrieved)
        if relevant else 1
    )

    # 필요한 근거가 검색됐는지
    context_recall = (
        1 if not need
        else len(need & retrieved_set) / len(need)
    )

    # 답변에 필요한 내용이 포함됐는지
    if need:
        used = sum(
            normalize(term) in answer
            for term in item["gold"]
        )

        context_utilization = used / len(item["gold"])

    else:
        context_utilization = int(
            "확인할수없" in answer
        )

    # 검색 Context가 답변의 숫자를 뒷받침하는지
    retrieved_text = " ".join(
        doc_map[chunk_id]["text"]
        for chunk_id in retrieved
    )

    answer_values = re.findall(
        r"\d+(?:\.\d+)?"
        r"(?:년|월|일|시간|개월|kg|gb|db|억|원|%)?",
        answer
    )

    faithfulness = int(
        all(
            value.lower() in retrieved_text.lower()
            for value in answer_values
        )
    )

    if not need:
        faithfulness = context_utilization

    # 인용이 정답 근거와 일치하는지
    citations = set(item["cite"])

    if need:
        citation = int(
            bool(citations)
            and citations.issubset(need)
        )
    else:
        citation = int(not citations)

    # JSON 형식 검사
    format_ok = 1

    if item["format"] == "json":
        try:
            json.loads(item["answer"])
        except json.JSONDecodeError:
            format_ok = 0

    # 실패 유형 판단
    if need and context_recall < 1:
        failure = "검색 실패"
        improvement = "Top-k 또는 검색 방식 개선"

    elif not need and context_utilization == 0:
        failure = "근거 사용 실패"
        improvement = "문서에 없으면 답변 보류"

    elif format_ok == 0:
        failure = "답변 형식 실패"
        improvement = "JSON 형식 검증"

    elif context_utilization == 0:
        failure = "생성 실패"
        improvement = "정답·숫자·제품명 재확인"

    elif context_utilization < 1:
        failure = "근거 사용 실패"
        improvement = "필요한 모든 근거 사용"

    elif citation == 0:
        failure = "인용 실패"
        improvement = "답변과 인용 Chunk 일치 확인"

    elif faithfulness == 0:
        failure = "근거 사용 실패"
        improvement = "검색 Context에 근거해서 답변"

    else:
        failure = "없음"
        improvement = "없음"

    # 정답 근거 원문
    evidence = " | ".join(
        f"{chunk_id}: {doc_map[chunk_id]['text']}"
        for chunk_id in item["need"]
    ) or "문서에 정답 없음"

    # 실제 검색 결과 원문
    search_result = " | ".join(
        f"{chunk_id}: {doc_map[chunk_id]['text']}"
        for chunk_id in retrieved
    )

    return [
        item["id"],
        item["type"],
        item["question"],
        evidence,
        search_result,
        item["answer"],
        round(context_relevance, 2),
        round(context_recall, 2),
        round(context_utilization, 2),
        faithfulness,
        citation,
        format_ok,
        failure,
        improvement
    ]


# ==================================================
# 6. 24개 질문 평가
# ==================================================

results = [
    evaluate(item)
    for item in questions
]


# ==================================================
# 7. result.csv 저장
# ==================================================

header = [
    "ID",
    "질문 유형",
    "평가 질문",
    "정답 근거",
    "검색 결과",
    "모델 답변",
    "Context Relevance",
    "Context Recall",
    "Context Utilization",
    "Faithfulness",
    "Citation",
    "Format",
    "실패 유형",
    "개선 방법"
]


with open(
    "result.csv",
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:
    csv.writer(f).writerows(
        [header] + results
    )


print(f"{len(results)}개 질문 평가 완료")
print("result.csv 저장 완료")