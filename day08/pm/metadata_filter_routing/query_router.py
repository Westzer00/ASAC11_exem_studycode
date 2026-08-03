ROUTES = [
    (
        "onboarding",
        ["신입사원", "첫 주", "온보딩"],
        ["Onboarding", "Security", "IT", "Support"],
    ),
    (
        "finance",
        ["출장", "출장비", "비용 정산", "정산", "영수증"],
        ["Finance", "Organization", "Support"],
    ),
    (
        "remote_work",
        ["재택근무", "원격근무", "집에서 회사"],
        ["Human Resources", "Security", "IT", "Support"],
    ),
    (
        "security_it",
        ["vpn", "gitlab", "비밀번호", "보안교육", "회사 시스템", "접속"],
        ["Security", "IT", "Support"],
    ),
    (
        "project",
        ["프로젝트", "jira", "confluence", "브랜치", "merge request"],
        ["Project", "IT", "Support"],
    ),
    (
        "hr",
        ["연차", "휴가", "반차", "병가", "근태"],
        ["Human Resources", "Support", "General"],
    ),
]
# 쿼리 라우터 함수 설정 -> e.g. 2번째 줄 키워드가 질문에있다면 -> 1번 라우터로 설정 => 3번째 줄에 있는 카테고리 내에서만 검색하기 !! 

def route_query(question: str) -> dict:
    question = question.lower()

    for route, keywords, categories in ROUTES:
        matched = [word for word in keywords if word in question]

        if matched:
            return {
                "route": route,
                "categories": categories,
                "matched_keywords": matched,
            }

    return {
        "route": "general",
        "categories": [],
        "matched_keywords": [],
    }