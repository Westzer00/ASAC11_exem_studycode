# 할 일 관리 API 명세서

## 1. 할 일 단건 조회

### 기본 정보

| 항목 | 내용 |
|---|---|
| 기능 | 특정 할 일 조회 |
| Method | GET |
| URL | /tasks/{taskId} |

### Path Parameter

| 이름 | 타입 | 필수 여부 | 설명 | 예시 |
|---|---|---|---|---|
| taskId | integer | 필수 | 조회할 할 일 ID | 1 |

### 성공 응답

- 상태 코드: `200 OK`

{
  "id": 1,
  "title": "HTTP 공부하기",
  "completed": false
}

### 실패 응답

#### 존재하지 않는 할 일

- 상태 코드: `404 Not Found`

{
  "code": "TASK_NOT_FOUND",
  "message": "해당 할 일을 찾을 수 없습니다."
}

#### 잘못된 요청값

- 상태 코드: `400 Bad Request`

{
  "code": "INVALID_TASK_ID",
  "message": "할 일 ID는 1 이상이어야 합니다."
}