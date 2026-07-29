# API 구현
```
POST   /tasks
GET    /tasks
GET    /tasks/{task_id}
PATCH  /tasks/{task_id}
DELETE /tasks/{task_id}
```

### 필수 구현 조건
- [x]Pydantic Model
- [x]올바른 상태 코드
- [x]없는 ID는 404
- [x]Router와 Service 분리
- [x]Swagger에서 실행 가능
- [x]요청 로그 기록

## 코드 구성
### main.py
* FastAPI 객체 생성
* Router 등록
* 요청 로그 Middleware
### router.py
* Pydantic 모델
* 5개 API endpoint
* 상태 코드
* 없는 ID의 404 처리
### service.py
* 메모리 저장소
* 생성·조회·수정·삭제 로직

http://127.0.0.1:8000/docs -> 링크를 통해 *Swagger* 화면에서 조작가능