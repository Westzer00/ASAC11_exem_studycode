# 공통 문서 Metadata Query Routing 실습
## 파일 구조 
### rag_dataset 공통 문서 구조
```
text
rag_dataset/
├── documents/
│   ├── 01_company_policy.txt
│   ├── 02_hr_policy.txt
│   ├── 03_security_policy.txt
│   ├── 04_it_system.txt
│   ├── 05_organization.txt
│   ├── 06_project_manual.txt
│   ├── 07_employee_handbook.txt
│   ├── 08_meeting_minutes.txt
│   ├── 09_business_trip_policy.txt
│   └── 10_faq.txt
│
├── metadata.csv
├── questions.csv
├── ground_truth.csv
├── parent_child.json
├── document_graph.json
└── README.md
```
### D 개인 실습 관련 문서 구조
```
pm/
├── rag_dataset/
├── metadata_filter_routing/
│   ├── results/
│   ├── query_router.py
│   ├── retriever.py
│   ├── evaluator.py
│   └── run_experiment.py
└── README.md
```
| 파일                  | 역할                             |
| ------------------- | ------------------------------ |
| `query_router.py`   | 질문의 Route와 검색 Category 결정      |
| `retriever.py`      | 문서 임베딩 생성 및 Dense Retrieval 수행 |
| `evaluator.py`      | Hit Rate, Recall@3, MRR 계산     |
| `run_experiment.py` | 전체 실험 실행 및 결과 저장               |


## 실행
`pip install pandas numpy sentence-transformers torch` 패키지 설치 

실행흐름
```
질문·정답 데이터 로드
→ 전체 문서 임베딩 생성
→ 기준 방식 검색
→ Query Routing
→ Metadata Filter 적용
→ 개선 방식 검색
→ 성능 평가
→ CSV 저장
```

## 평가지표
| 지표           | 설명                            |
| ------------ | ----------------------------- |
| Hit Rate     | Top-3에 정답 문서가 하나라도 포함된 질문의 비율 |
| Recall@3     | 전체 정답 문서 중 Top-3에서 검색된 비율     |
| MRR          | 가장 먼저 검색된 정답 문서 순위의 역수 평균     |
| Latency      | 질문당 평균 검색 시간                  |
| Search Calls | 질문당 검색 호출 횟수                  |
| LLM Calls    | Router에서 사용한 LLM 호출 횟수        |
| Token Usage  | LLM 사용 Token 수                |


=>현재 구현은 키워드 Router를 사용하므로 LLM Calls와 Token Usage는 0

## 결과
### results.csv

* 정답 문서
* Baseline Top-3
* 선택된 Route
* 필터 이후 후보 문서 수
* Improved Top-3
* 질문별 Hit, Recall@3, RR
* 검색 지연 시간
* 실패 원인과 필터 부작용

### summary.csv
전체 질문의 평균 성능 비교
| Method                    | Hit Rate | Recall@3 |      MRR | 평균 지연 시간 |
| ------------------------- | -------: | -------: | -------: | -------: |
| Baseline                  | 실행 결과 입력 | 실행 결과 입력 | 실행 결과 입력 | 실행 결과 입력 |
| Metadata Filter + Routing | 실행 결과 입력 | 실행 결과 입력 | 실행 결과 입력 | 실행 결과 입력 |


### 결과 해석

1. Metadata Filter 적용 후 Hit Rate와 Recall@3가 증가했는가?
2. 정답 문서가 더 높은 순위에 검색되어 MRR이 증가했는가?
3. 검색 후보 감소로 지연 시간이 줄었는가?
4. 잘못된 Routing으로 정답 문서가 후보에서 제외되었는가?

> Metadata Filter는 관련 없는 문서를 제거하여 검색 순위를 높일 수 있음 !! 
> 반대로 잘못된 Route를 선택하면 정답 문서가 검색 전에 제외되어 Recall@3가 낮아질 수 있음 !! 