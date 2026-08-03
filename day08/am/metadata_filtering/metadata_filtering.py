import csv
import json
from pathlib import Path

# 현재 파이썬 파일이 있는 폴더
BASE_DIR = Path(__file__).parent

# 입력 Json 파일 경로
DOCUMENTS_PATH = BASE_DIR / "documents.json"

# 출력 CSV 파일 경로
RESULTS_PATH = BASE_DIR / "results.csv"

#json 파일 열기 -> 내용읽기 -> 리스트로 반환
def load_documents() -> list[dict]:
    """documents.json 파일을 읽어와서 문서 목록을 읽고 리스트로 반환합니다.""" 

    with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f: # r 읽기 모드로, 파일을 열겠다 # with사용시 자동으로 파일 닫힘
        documents = json.load(f) # json.load() : json 파일을 읽어서 파이썬 객체로 변환
    return documents

def filter_documents(
    documents: list[dict], # 입력1, 전체 문서 목록
    metadata_filter: dict # 입력2, 적용한 검색 조건
) -> list[dict]: # 반환값, 조건에 맞는 문서 목록
    """Metadata 조건을 모두 만족하는 문서만 반환한다."""

    results =[]

    for document in documents: # 전체 문서 목록에서 하나씩 꺼내서
        matched = True # 조건을 만족하는지 여부를 나타내는 변수, 초기값 True

        for key, expected_val in metadata_filter.items(): #딕셔너리의 키와 값을 한쌍씩 반환 !! 
            acutal_value = document.get(key) # document 딕셔너리에서 key에 해당하는 값을 가져옴

            if acutal_value != expected_val: #실제 문서값과 필터 조건값이 다른지를 검사 !!!!! 
                matched = False # 조건을 만족하지 않으니까 
                break

        if matched: # 모든조건을 만족하면
            results.append(document) # 결과 리스트에 추가

    return results

def save_results(results: list[dict]) -> None: #반환값 없는 함수, csv로 저장할꺼니까 반환값 필요 없움
    """필터링 결과를 CSV 파일로 저장한다"""

    fieldnames = [
        "document_id",
        "title",
        "department",
        "document_type",
        "version",
        "security_level",
    ]

    with open(
        RESULTS_PATH,
        "w", # 기존 파일 있을경우 덮어쓰기 !! 쓰기 모드임 
        encoding="utf-8-sig",
        newline="", # csv 저장시, 빈줄 생기는거 방지
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader() #첫번째 열 이름을 헤더로 작성 -> fieldnames에 정의된 값

        for result in results: # 결과 리스트에서 하나씩 꺼내서
            row ={}

            for fieldname in fieldnames: # fieldnames에 정의된 값들을 하나씩 꺼내서
                row[fieldname] = result.get(fieldname, "") # 결과 딕셔너리에서 fieldname에 해당하는 값을 가져옴, 없으면 빈 문자열
                writer.writerow(row) # 각 행을 CSV 파일에 쓰기

def main() -> None:
    """메인 함수, 전체 Metadata Filtering 과정을 실행한다."""

    # 1. 문서 불러오기
    documents = load_documents()

    print(f"전체 문서 수: {len(documents)}개")

    # # 2. Metadata 검색 조건 설정
    # metadata_filter = {
    #     "department": "AI",
    #     "document_type": "deployment-guide",
    #     "version": "2.1",
    # }
    # print("\n적용한 Metadata Filter")
    #     print(metadata_filter)

# ==================================================================================================================================================

    # 2-1. Metadata 검색 조건을 사용자 입력으로 받기

    # 부서 선택
    print("\n[부서 선택]")
    print("0. 전체")
    print("1. AI")
    print("2. HR")
    print("3. Development")

    department_choice = input("번호 입력: ").strip()

    department_options = {
        "0": None,
        "1": "AI",
        "2": "HR",
        "3": "Development",
    }

    selected_department = department_options.get(department_choice)

    if department_choice not in department_options:
        print("부서 번호를 잘못 입력했습니다.")
        return


    # 버전 선택
    print("\n[버전 선택]")
    print("0. 전체")
    print("1. 1.0")
    print("2. 1.2")
    print("3. 2.1")
    print("4. 3.0")

    version_choice = input("번호 입력: ").strip()

    version_options = {
        "0": None,
        "1": "1.0",
        "2": "1.2",
        "3": "2.1",
        "4": "3.0",
    }

    selected_version = version_options.get(version_choice)

    if version_choice not in version_options:
        print("버전 번호를 잘못 입력했습니다.")
        return


    # 보안 등급 선택
    print("\n[보안 등급 선택]")
    print("0. 전체")
    print("1. public")
    print("2. internal")
    print("3. confidential")

    security_choice = input("번호 입력: ").strip()

    security_options = {
        "0": None,
        "1": "public",
        "2": "internal",
        "3": "confidential",
    }

    selected_security = security_options.get(security_choice)

    if security_choice not in security_options:
        print("보안 등급 번호를 잘못 입력했습니다.")
        return

    # 선택한 조건만 Metadata Filter에 추가
    metadata_filter = {}

    if selected_department is not None:
        metadata_filter["department"] = selected_department

    if selected_version is not None:
        metadata_filter["version"] = selected_version

    if selected_security is not None:
        metadata_filter["security_level"] = selected_security


# ==================================================================================================================================================

    # 3. Metadata Filtering 수행
    results = filter_documents(
        documents=documents, 
        metadata_filter=metadata_filter,
    )

    # 4. 결과 출력
    print(f"\n조건에 맞는 문서 수: {len(results)}개")

    for result in results:
       print(
            f"- [{result['document_id']}] "
            f"{result['title']}"
        )

    # 5. 결과 저장
    save_results(results) 

    print(f"\n결과를 CSV 파일로 저장 완료 ! : {RESULTS_PATH}")

# 현재 파일을 직접 실행할 경우에만, main() 함수를 실행하도록 함
if __name__ == "__main__": 
    main()
