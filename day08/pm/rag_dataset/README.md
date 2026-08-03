# RAG Retrieval Evaluation Dataset

## 1. 프로젝트 목적

본 데이터셋은 다양한 Retrieval 기법의 성능을 동일한 환경에서 비교하기 위해 제작되었습니다.

모든 팀은 **동일한 문서와 동일한 질문**을 사용하며,
검색(Retrieval) 방식만 다르게 구현하여 성능을 비교합니다.

---

# 2. 데이터셋 구조

```text
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

---

# 3. 문서 설명

| 파일 | 설명 |
|------|------|
| Company Policy | 회사 공통 정책 |
| HR Policy | 휴가, 근태, 재택근무 |
| Security Policy | 보안 정책, VPN |
| IT System Guide | Jira, GitLab, Confluence |
| Organization Guide | 조직도 및 승인 권한 |
| Project Manual | 프로젝트 운영 절차 |
| Employee Handbook | 신입사원 온보딩 |
| Meeting Minutes | 프로젝트 회의록 |
| Business Trip Policy | 출장 및 비용 정산 |
| FAQ | 자주 묻는 질문 |

---

# 4. 공통 평가 방법

모든 팀은 아래 파일을 동일하게 사용합니다.

- documents/
- questions.csv
- ground_truth.csv

질문을 변경하거나 추가하지 않습니다.

---

# 5. 팀별 구현 내용

모든 팀은 동일한 문서(documents)와 동일한 질문(questions.csv)을 사용합니다.

각 팀은 담당 Retrieval 기법만 구현하여 성능을 비교합니다.

---

## A팀

### 담당 기법

- Query Rewrite
- Multi-query Retrieval

### 설명

질문을 더 검색하기 좋은 형태로 변환하거나,
하나의 질문을 여러 개의 검색 Query로 생성하여 검색 성능을 향상시킵니다.

예시

질문

```
집에서 회사 시스템을 사용하려면?
```

↓

Query Rewrite

```
재택근무
VPN
원격근무
회사 시스템 접속
```

↓

Multi-query

```
재택근무 방법
VPN 사용 방법
원격 접속 절차
```

↓

검색

↓

LLM

---

## B팀

### 담당 기법

- Query Decomposition
- HyDE (Hypothetical Document Embeddings)

### 설명

복합 질문을 여러 개의 하위 질문으로 분해하거나,
가상의 정답 문서를 생성한 후 그 문서를 이용해 Retrieval 성능을 높입니다.

예시

질문

```
해외 출장 승인 절차와 출장 후 해야 할 일을 알려주세요.
```

↓

분해

```
① 해외 출장은 누가 승인하는가?

② 출장 후 해야 하는 일은 무엇인가?
```

↓

각각 검색

↓

검색 결과 병합

↓

LLM

---

## C팀

### 담당 기법

- Hybrid Retrieval

### 설명

BM25(키워드 검색)와 Dense Retrieval(임베딩 검색)을 함께 사용하여 검색 정확도를 높입니다.

예시

```
BM25

+

Dense Retrieval

↓

점수 결합

↓

Top-K 선정

↓

LLM
```

---

## D팀

### 담당 기법

- Metadata Filter
- Routing

### 설명

문서의 메타데이터(부서, 문서 유형, 작성일 등)를 활용하여 검색 범위를 제한하거나,
질문의 종류에 따라 적절한 문서 컬렉션으로 Routing합니다.

예시

질문

```
출장비는 언제 정산해야 하나요?
```

↓

Metadata Filter

```
부서 = Finance

문서유형 = Policy
```

↓

Business Trip Policy 검색

↓

LLM

또는

질문

```
비밀번호 정책이 뭐야?
```

↓

Security 문서로 Routing

↓

검색

↓

LLM

---

## E팀

### 담당 기법

- Parent-Child Retrieval
- Multi-hop Retrieval

### 설명

Parent-Child Retrieval은 작은 Chunk로 검색하고,
큰 Parent 문맥을 함께 전달하여 답변 품질을 높입니다.

Multi-hop Retrieval은 여러 문서를 순차적으로 검색하여
최종 답변을 생성합니다.

예시

질문

```
신입사원이 재택근무를 하려면 무엇이 필요한가?
```

↓

Employee Handbook 검색

↓

Security Policy 검색

↓

IT System Guide 검색

↓

최종 답변 생성
