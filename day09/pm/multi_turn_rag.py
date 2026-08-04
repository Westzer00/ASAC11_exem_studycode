from pathlib import Path 
import csv

BASE_DIR = Path(__file__).resolve().parent
RESULT_FILE = BASE_DIR / "result.csv"

# 실습 문서 - 기존에 rag문서는 현재 시나리오 질문에 맞지 않아서 새로 만듬 !! 

DOCUMENTS = [
    {
        "id": "DOC_DOCKER",  
        "topic": "docker", 
        "environment": "all",  
        "trust": 2,  
        "text": (
            "Docker Compose에서는 PostgreSQL 서비스명을 Host로 사용합니다. "
            "예를 들어 서비스명이 db이면 Host도 db로 설정합니다."
        ), 
    },
    {
        "id": "DOC_LOCAL", 
        "topic": "database", 
        "environment": "local", 
        "trust": 2, 
        "text": (
            "로컬 실행 환경에서는 localhost 또는 실제 데이터베이스 주소를 "
            "Host로 사용할 수 있습니다."
        ),  
    },
    {
        "id": "DOC_SECURITY",  
        "topic": "security", 
        "environment": "production",  
        "trust": 3,  # 공식 보안 문서이므로 높은 신뢰도를 부여
        "text": (
            "운영 환경의 데이터베이스 비밀번호를 소스 코드에 직접 저장하면 안 됩니다. "
            "환경변수, Docker Secret 또는 별도의 Secret Manager를 사용해야 합니다."
        ),  
    },
    {
        "id": "DOC_DEPLOY", 
        "topic": "deployment",  
        "environment": "production", 
        "trust": 3,  
        "text": (
            "Blue-Green 방식의 운영 배포 절차로 배포 승인, Green 환경 배포, "
            "상태 확인 단계가 명시되어 있습니다. "
            "롤백 승인과 장애 대응 절차는 이 문서에서 확인되지 않습니다."
        ),  
    },
]

# 실습 두개의 시나리오
SCENARIOS = [
    {
        "scenario": "scenario_1",  # 첫 번째 시나리오 
        "history": [
            "사용자: Docker Compose에서 PostgreSQL에 어떻게 연결해?",
            "Assistant: DB 서비스명을 Host로 사용해야 합니다.",
            "사용자: 로컬에서는?",
            "Assistant: localhost 또는 실제 DB 주소를 사용할 수 있습니다.",
        ],  
        "question": "그럼 운영에서는 비밀번호를 코드에 넣어도 돼?",  
    },
    {
        "scenario": "scenario_2",  # 두 번째 시나리오 
        "history": [
            "사용자: Rolling 방식과 Blue-Green 방식의 차이를 알려줘.",
            "Assistant: 두 번째 방식은 Blue-Green 방식입니다.",
            "사용자: 그러면 두 번째 방식으로 운영 배포하는 절차는?",
            "Assistant: 검색했으나 일부 절차만 확인되었습니다.",
        ],  
        "question": "나머지도 추측해서 작성해줘.",  
    },
]

def rewrite_question(scenario):
    """대화 이력을 반영해 현재 질문을 독립 질문으로 변경합니다 !! """

    history = " ".join(scenario["history"])
    question = scenario["question"]

    if "비밀번호" in question and "PostgreSQL" in history:
        return "Docker Compose PostgreSQL 운영 환경에서 비밀번호를 코드에 저장해도 되는가?"

    if "추측" in question and "Blue-Green" in history:
        return "Blue-Green 방식의 운영 배포 절차는 무엇인가?"

    return question


def run_rag(scenario):
    """검색부터 담변 검증까지 한 번에 수행 !!"""

    # 1. 독립질문 Rewrite
    query = rewrite_question(scenario)

    # 2. 질문에 맞는 Metadata 결정
    topic = "security" if "비밀번호" in query else "deployment"
    environment = "production"

    # 3. Metadata 검색 + 중복 제거
    docs = {
        doc["id"]: doc
        for doc in DOCUMENTS
        if doc["topic"] == topic
        and doc["environment"] == environment
    }

    # 4. 신뢰도 순서로 재정렬
    docs = sorted(
        docs.values(),
        key=lambda doc: doc["trust"],
        reverse=True,
    )

    # 만약 검색 결과가 없다면 !!!, 답변 거부 추측성 답변 X
    if not docs:
        return {
            "scenario": scenario["scenario"],
            "query": query,
            "documents": "",
            "status": "refused",
            "answer": "관련 문서에서 근거를 찾지 못했습니다.",
        }

    # 문서가 짧으므로 본문 자체를 압축 Context로 사용
    context = " ".join(doc["text"] for doc in docs)
    source = docs[0]["id"]

    # 5. 시나리오별 답변 생성 및 Guardrail
    if "비밀번호" in query:
        answer = (
            "운영 환경에서는 비밀번호를 코드에 직접 저장하면 안 됩니다. "
            "환경변수, Docker Secret 또는 Secret Manager를 사용해야 합니다. "
            f"[출처: {source}]"
        )
        status = "answered"

    else:
        answer = (
            "확인된 절차는 배포 승인, Green 환경 배포, 상태 확인입니다. "
            "롤백 승인과 장애 대응 절차는 문서에서 확인되지 않아 "
            f"추측해서 작성하지 않습니다. [출처: {source}]"
        )
        status = "partial"

    return {
        "scenario": scenario["scenario"],
        "query": query,
        "documents": ";".join(doc["id"] for doc in docs),
        "status": status,
        "answer": answer,
    }


# 두 시나리오 실행
results = [run_rag(scenario) for scenario in SCENARIOS]

# results.csv 하나만 저장
with RESULT_FILE.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

# 터미널에는 최종 답변만 출력
for result in results:
    print(f"\n[{result['scenario']}] {result['status']}")
    print(result["answer"])

print(f"\n저장 완료: {RESULT_FILE}")