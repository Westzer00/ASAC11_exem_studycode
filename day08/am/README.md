# Metadata Filtering·Query Routing

## 파일 구조
```
day08_llm/
├── metadata_filtering/
│   ├── documents.json
│   ├── metadata_filtering.py
│   └── metadata_result.csv
│
├── query_routing/
│   ├── questions.json
│   ├── query_routing.py
│   └── routing_result.csv
│
└── README.md
```
### 각 실습의 목표
| 실습                 | 입력        | 처리                   | 출력                    |
| ------------------ | --------- | -------------------- | --------------------- |
| Metadata Filtering | 문서와 필터 조건 | Metadata가 일치하는 문서 선택 | `metadata_result.csv` |
| Query Routing      | 질문 20개    | 키워드로 질문 유형 분류        | `routing_result.csv`  |
