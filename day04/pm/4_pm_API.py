import csv
import os
import time
from pathlib import Path

from dotenv import load_dotenv #환경변수 읽어오기 위해서
from google import genai
from google.genai import errors, types


# 1. 환경변수 불러오기
BASE_DIR = Path(__file__).resolve().parent #지금 파일의 폴더 가져오기
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

if not API_KEY or not MODEL:
    raise RuntimeError(".env의 GEMINI_API_KEY와 GEMINI_MODEL을 확인하세요.")

client = genai.Client(api_key=API_KEY)


# 2. 테스트 데이터
TEST_DATA = [
    {"text": "배송도 빠르고 제품도 만족스럽다.", "label": "긍정"},
    {"text": "가격에 비해 품질이 훌륭하다.", "label": "긍정"},
    {"text": "사용한 지 하루 만에 고장 났다.", "label": "부정"},
    {"text": "설명과 실제 제품이 너무 다르다.", "label": "부정"},
    {"text": "제품은 어제 오후에 도착했다.", "label": "중립"},
    {"text": "제품의 무게는 500그램이다.", "label": "중립"},
]

LABELS = ["긍정", "부정", "중립"]
TEMPERATURES = [0.0, 0.8]
# 0.0 → 상대적으로 안정적이고 일관된 출력
# 0.8 → 상대적으로 다양하고 무작위성이 높은 출력


# 3. 프롬프트 만들기
def make_prompt(prompt_type, text):
    if prompt_type == "simple":
        return f"다음 문장의 감정을 분류해줘.\n문장: {text}"

    if prompt_type == "clear":
        return f"""
다음 문장을 긍정, 부정, 중립 중 하나로 분류하세요.
반드시 분류 결과 하나만 출력하세요.

#Few-shot
문장: {text} 
""".strip() #빈 문자열 제거

    return f"""
다음 문장을 긍정, 부정, 중립 중 하나로 분류하세요.
반드시 분류 결과 하나만 출력하세요.

예시:
문장: 성능이 좋고 사용하기 편하다.
답변: 긍정

문장: 작동이 자주 멈춘다.
답변: 부정

문장: 제품은 월요일에 도착했다.
답변: 중립

문장: {text}
답변:
""".strip()


# 4. 모델 응답에서 라벨 찾기
def extract_label(output): #긍부중 중에 1개 찾아서 출력하는 함수
    for label in LABELS:
        if label in output:
            return label

    return "" # 라벨이 없으면 빈 문자열 반환 -> 오답 처리


# 5. CSV 저장
def save_results(results):
    path = BASE_DIR / "results.csv"

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "prompt_type",
                "temperature",
                "text",
                "answer",
                "output",
                "prediction",
                "correct",
                "format_ok",
                "response_length",
                "wrong_info_manual",
            ],
        )

        writer.writeheader()
        writer.writerows(results)


# 6. 실험 실행
# 6개 조건 × 문장 6개 = 총 36회
def main():
    results = []
    prompt_types = ["simple", "clear", "few_shot"]

    for prompt_type in prompt_types:
        for temperature in TEMPERATURES:
            for item in TEST_DATA:
                print(
                    f"실행 중: {prompt_type}, "
                    f"temperature={temperature}, "
                    f"{item['text']}"
                )

                prompt = make_prompt(prompt_type, item["text"])

                try:
                    response = client.models.generate_content(
                        model=MODEL,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=20,
                        ),
                    )

                    output = (response.text or "").strip()

                except errors.APIError as error:
                    print(f"API 오류: {error.code} - {error.message}")

                    # 지금까지 결과 저장
                    save_results(results)
                    return

                prediction = extract_label(output)

                results.append(
                    {
                        "prompt_type": prompt_type,
                        "temperature": temperature,
                        "text": item["text"],
                        "answer": item["label"],
                        "output": output,
                        "prediction": prediction,
                        "correct": prediction == item["label"],
                        "format_ok": output in LABELS,
                        "response_length": len(output),
                        "wrong_info_manual": "",
                    }
                )

                save_results(results)
                time.sleep(10)

    # 7. 결과 요약 출력
    print("\n=== 실험 결과 ===")

    for prompt_type in prompt_types:
        for temperature in TEMPERATURES:
            group = [
                row
                for row in results
                if row["prompt_type"] == prompt_type
                and row["temperature"] == temperature
            ]

            accuracy = sum(row["correct"] for row in group) / len(group) * 100
            format_rate = sum(row["format_ok"] for row in group) / len(group) * 100
            avg_length = sum(row["response_length"] for row in group) / len(group)

            print(
                f"{prompt_type:8} | "
                f"Temp={temperature} | "
                f"정확도={accuracy:.1f}% | "
                f"형식 준수율={format_rate:.1f}% | "
                f"평균 길이={avg_length:.1f}자"
            )

    print("\nresults.csv 저장 완료")


if __name__ == "__main__":
    main()