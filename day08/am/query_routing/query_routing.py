import csv
import json
from pathlib import Path

# 현재 파일 경로 설정
BASE_DIR = Path(__file__).parent
QUESTION_PATH = BASE_DIR / "questions.json"
RESULT_PATH = BASE_DIR / "results.csv"

# 각 Route에 대한 설명
ROUTE_DETAILS = {
        "검색 불필요": {
        "reason": "현재 질문과 사용자가 제공한 정보만으로 처리할 수 있습니다.",
        "problem": "불필요한 검색으로 비용과 응답 시간이 증가할 수 있습니다.",
        "fallback": "검색 없이 LLM이 직접 응답합니다.",
    },
    "문서 검색": {
        "reason": "규정, 절차, 가이드 등 비정형 문서의 내용이 필요합니다.",
        "problem": "DB나 웹으로 잘못 전달하면 회사 내부 기준과 다른 답변이 생성될 수 있습니다.",
        "fallback": "키워드 검색 또는 관련 부서 담당자에게 문의합니다.",
    },
    "DB 조회": {
        "reason": "사용자 수, 매출, 재고 등 정확한 정형 데이터 조회가 필요합니다.",
        "problem": "문서 검색 결과에 기록된 과거 값을 현재 데이터로 잘못 사용할 수 있습니다.",
        "fallback": "최근 통계 보고서 또는 데이터 Snapshot을 사용합니다.",
    },
    "웹 검색": {
        "reason": "뉴스, 환율, 버전 등 최신 외부 공개 정보가 필요합니다.",
        "problem": "내부 문서나 모델의 오래된 지식으로 답변할 수 있습니다.",
        "fallback": "공식 사이트 또는 공식 API를 조회합니다.",
    },
    "여러 데이터 소스 검색": {
        "reason": "질문에 서로 다른 종류의 정보가 함께 필요합니다.",
        "problem": "하나의 데이터 소스만 사용하면 일부 정보가 누락된 답변이 생성됩니다.",
        "fallback": "조회에 성공한 데이터만 사용하고 누락된 항목을 명시합니다.",
    },
}

def load_questions() -> list[dict]: #반환값이 딕셔너리가 들어가있는 리스트로 !!!! 
    """questions.json 파일을 읽어와서 질문 목록을 읽고 리스트로 반환합니다.""" 

    try: # 파일이 없는 경우, 문법오류등의 오류발생 확률이 존재함으로 예외처리
        with open(QUESTION_PATH, "r", encoding="utf-8") as f: 
            questions = json.load(f)

        return questions
    except FileNotFoundError:
        print(f"Error: {QUESTION_PATH} 파일을 찾을 수 없습니다.")
        return []
    except json.JSONDecodeError:
        print(f"Error: {QUESTION_PATH} 파일의 JSON 형식이 잘못되었습니다.")
        return []

# =============================핵심함수=============================

def route_query(question: str) -> tuple[str,list[str]]: 
    """
    질문의 키워드를 분석하여 사용할 데이터 소스를 선택한다.

    반환값:
        route: 최종 분류 결과
        selected_sources: 실제 선택된 데이터 소스 목록
    """

    # 문서 검색과 관련된 키워드
    document_keywords = [
        "규정",
        "절차",
        "가이드",
        "매뉴얼",
        "정책",
        "기준",
        "인증 방식",
        "배포 방법",
        "장애 원인",
        "고객 불만",]

    # DB 조회와 관련된 키워드
    database_keywords = [
        "가입자 수",
        "사용자 수",
        "매출",
        "재고",
        "몇 건",
        "남은 연차",
        "잔여 연차",
        "오류 발생 건수",
        "출장 비용",
        "비용 내역",
    ]
    # 웹 검색과 관련된 표현
    web_keywords = [
        "오늘 발표된",
        "AI 뉴스",
        "현재 원달러 환율",
        "현재 환율",
        "최신 안정 버전",
        "경쟁사",
        "최근 출시",
        "제품의 가격",
    ]

    # 검색이 필요하지 않은 표현
    no_search_keywords = [
        "안녕하세요",
        "곱하면",
        "계산해줘",
        "정중하게 바꿔줘",
        "요약해줘",
    ]

    selected_sources = [] # 선택된 데이터 소스 저장할 빈 리스트 !! 

    # 문서 검색이 필요한지 확인
    if any(keyword in question for keyword in document_keywords):
        selected_sources.append("문서 Vector DB")

    # DB 조회가 필요한지 확인
    if any(keyword in question for keyword in database_keywords):
        selected_sources.append("SQL DB")

    # 웹 검색이 필요한지 확인
    if any(keyword in question for keyword in web_keywords):
        selected_sources.append("웹 검색")

    # 두 개 이상의 데이터 소스가 선택된 경우
    if len(selected_sources) >= 2:
        return "여러 데이터 소스 검색", selected_sources

    # 한 개의 데이터 소스가 선택된 경우
    if len(selected_sources) == 1:
        selected_source = selected_sources[0]

        if selected_source == "문서 Vector DB":
            return "문서 검색", selected_sources

        if selected_source == "SQL DB":
            return "DB 조회", selected_sources

        if selected_source == "웹 검색":
            return "웹 검색", selected_sources

    # 검색 불필요 키워드가 포함된 경우
    if any(keyword in question for keyword in no_search_keywords):
        return "검색 불필요", ["검색 없음"]

    # 어떤 규칙에도 해당하지 않는 경우
    return "검색 불필요", ["검색 없음"]

def create_result(item:dict) -> dict: # 질문 하나를 받아, 최종 결과를 만드는 함수
    """질문 하나를 Routing하고 결과 행을 생성한다."""

    question = item["question"] # item에서 질문 하나 꺼내기

    route, selected_sources = route_query(question) # 질문을 Routing하고 결과 받기 # route_query()가 두 값을 반환하므로 각각 나눠서 받rl

    route_detail = ROUTE_DETAILS[route]  # json에서 route에 대한 상세 설명 가져오기

    return {
        "id": item["id"],
        "question": question,
        "route": route,
        "selected_sources": ", ".join(selected_sources),
        "reason": route_detail["reason"],
        "wrong_routing_problem": route_detail["problem"],
        "fallback": route_detail["fallback"],
    }

def save_results(results: list[dict]) -> None: # CSV 저장 함수
    """Routing 결과를 CSV 파일로 저장한다."""

    fieldnames = [
        "id",
        "question",
        "route",
        "selected_sources",
        "reason",
        "wrong_routing_problem",
        "fallback",
    ]

    with open(RESULT_PATH, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

def print_results(results: list[dict]) -> None: # 결과 출력 함수
    """Routing 결과를 콘솔에 출력한다."""

    print("=" * 70)
    print(f"ID            : {results['id']}")
    print(f"질문          : {results['question']}")
    print(f"분류          : {results['route']}")
    print(f"데이터 소스   : {results['selected_sources']}")
    print(f"선택 근거     : {results['reason']}")
    print(f"오분류 문제   : {results['wrong_routing_problem']}")
    print(f"Fallback      : {results['fallback']}")

def main() -> None: # main 함수
    """전체 질문을 라우팅 하고 결과를 출력&저장"""

    #1. 질문 목록 불러오기
    questions = load_questions()

    if not questions:
        print("질문 목록이 비어 있습니다. 프로그램을 종료합니다.")
        return
    print(f"전체 질문 수: {len(questions)}개")

    # 2. 각 질문을 라우팅하고 결과 생성
    results = []

    for item in questions:
        result = create_result(item)
        results.append(result)

        print_results(result)


    # 3. 결과를 CSV 파일로 저장
    save_results(results)

    # 4. 분류 개수 출력
    route_counts = {}

    for result in results:
        route = result["route"]
        route_counts[route] = route_counts.get(route, 0) + 1

    print("\n" + "=" * 70)
    print("분류 결과 요약")

    for route, count in route_counts.items():
        print(f"- {route}: {count}개")

    print(f"\n결과 저장 완료: {RESULT_PATH}")


if __name__ == "__main__": # main 함수 실행
    main()