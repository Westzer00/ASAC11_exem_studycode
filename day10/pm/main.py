import csv
from questions import DATA


# 사람이 직접 평가한 RAG 답변 점수
HUMAN_SCORE = [
    4, 5, 1, 5, 1,
    4, 1, 5, 5, 5,
    5, 5, 5, 5, 5,
    5, 2, 4, 5, 1,
]

# 실험 1: Judge에게 점수만 요청한 결과
SCORE_ONLY = [
    5, 5, 1, 5, 1,
    5, 1, 5, 5, 5,
    5, 5, 5, 5, 5,
    5, 2, 5, 5, 1,
]

# 실험 2: Judge에게 점수와 근거를 함께 요청한 결과
LLM_SCORE = [
    4, 5, 1, 5, 1,
    5, 1, 5, 5, 5,
    5, 5, 5, 5, 5,
    5, 3, 4, 5, 1,
]

JUDGE_REASON = [
    "원격 접속과 명령 실행은 맞지만 파일 전송 설명이 빠졌다.",
    "Client와 Server의 역할을 정확하게 구분했다.",
    "IP와 Port의 역할을 반대로 설명했다.",
    "-p 옵션의 역할을 정확하게 설명했다.",
    "-v를 Port 변경 옵션으로 잘못 설명했다.",
    "두 인증 방식의 핵심 차이를 정확하게 설명했다.",
    "Private Key와 Public Key의 보관 위치가 반대다.",
    "SSH Config의 목적을 정확하게 설명했다.",
    "현재 사용자 계정을 확인한다는 설명이 정확하다.",
    "현재 시스템의 호스트 이름을 확인한다는 설명이 정확하다.",
    "현재 작업 디렉터리의 절대 경로를 정확하게 설명했다.",
    "프로세스와 PID의 관계를 정확하게 설명했다.",
    "LISTEN 상태의 의미를 정확하게 설명했다.",
    "두 바인딩 주소의 접근 범위를 정확하게 구분했다.",
    "tail 명령과 -n 100 옵션의 의미가 정확하다.",
    "grep의 -i와 -n 옵션을 정확하게 설명했다.",
    "일부 관련 내용은 있지만 실제 요청 응답 확인이라는 핵심이 빠졌다.",
    "헤더와 본문은 맞지만 HTTP 상태 줄 설명이 빠졌다.",
    "로컬 파일을 원격 서버로 전송한다는 설명이 정확하다.",
    "timed out과 refused의 의미를 반대로 설명했다.",
]

# 실험 3: A=RAG 답변, B=비교 답변
PAIR_AB = [
    "B", "A", "B", "A", "B",
    "A", "B", "A", "A", "A",
    "A", "A", "A", "A", "A",
    "A", "B", "A", "A", "B",
]

# 사람이 직접 선택한 Pairwise 결과
HUMAN_PAIRWISE = [
    "TIE", "A", "B", "A", "B",
    "A", "B", "A", "A", "A",
    "A", "A", "A", "A", "A",
    "A", "B", "A", "A", "B",
]

# 실험 4: 순서를 바꿔 A=비교 답변, B=RAG 답변으로 평가
PAIR_BA_RAW = [
    "A", "B", "A", "B", "A",
    "B", "A", "A", "B", "B",
    "B", "B", "B", "B", "B",
    "B", "A", "A", "B", "A",
]

# 실험 5: A=짧은 답변, B=긴 답변
LENGTH_WINNER = ["LONG"] * 20

HUMAN_LENGTH = [
    "LONG", "LONG", "LONG", "LONG", "LONG",
    "LONG", "LONG", "LONG", "TIE", "TIE",
    "TIE", "LONG", "LONG", "LONG", "TIE",
    "LONG", "LONG", "LONG", "LONG", "LONG",
]


def reverse_winner(winner):
    """순서를 바꾼 결과를 원래 A/B 기준으로 복원한다."""
    return {
        "A": "B",
        "B": "A",
        "TIE": "TIE",
    }[winner]


rows = []

for index, data in enumerate(DATA):
    pair_ba_normalized = reverse_winner(PAIR_BA_RAW[index])

    rows.append({
        "id": index + 1,
        **data,
        "human_score": HUMAN_SCORE[index],
        "score_only": SCORE_ONLY[index],
        "llm_score": LLM_SCORE[index],
        "judge_reason": JUDGE_REASON[index],
        "human_pairwise": HUMAN_PAIRWISE[index],
        "pair_ab": PAIR_AB[index],
        "pair_ba_raw": PAIR_BA_RAW[index],
        "pair_ba_normalized": pair_ba_normalized,
        "human_length": HUMAN_LENGTH[index],
        "length_winner": LENGTH_WINNER[index],
    })


# 전체 데이터를 CSV로 저장
with open("results.csv", "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)


count = len(rows)

exact_match = sum(
    row["human_score"] == row["llm_score"]
    for row in rows
) / count

within_one = sum(
    abs(row["human_score"] - row["llm_score"]) <= 1
    for row in rows
) / count

mae = sum(
    abs(row["human_score"] - row["llm_score"])
    for row in rows
) / count

prompt_consistency = sum(
    row["score_only"] == row["llm_score"]
    for row in rows
) / count

order_consistency = sum(
    row["pair_ab"] == row["pair_ba_normalized"]
    for row in rows
) / count

pairwise_agreement = sum(
    row["human_pairwise"] == row["pair_ab"]
    for row in rows
) / count

length_agreement = sum(
    row["human_length"] == row["length_winner"]
    for row in rows
) / count


print("=== Pointwise / Pairwise Judge 실습 결과 ===")
print(f"사람 평가와 정확히 일치율: {exact_match:.1%}")
print(f"±1점 이내 일치율: {within_one:.1%}")
print(f"평균 절대 오차: {mae:.2f}")
print(f"점수만 출력 vs 근거 포함 동일률: {prompt_consistency:.1%}")
print(f"Pairwise 답변 순서 일관성: {order_consistency:.1%}")
print(f"Pairwise 사람 평가 일치율: {pairwise_agreement:.1%}")
print(f"긴 답변/짧은 답변 사람 평가 일치율: {length_agreement:.1%}")
print("결과 저장 완료: results.csv")