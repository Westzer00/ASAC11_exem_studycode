# Fastapi - postgres
## 파일 구조
```
fastapi-postgres/
├── main.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
└── .env
```
## 프로그램 흐름
```
내 PC :8000
    ↓
app · FastAPI
    ↓ db:5432
db · PostgreSQL
    ↓
db_data Volume
```
```
내 PC
│
│  http://localhost:8000
▼
┌──────────────────────────────┐
│ Docker Compose 전용 Network   │
│                              │
│  ┌──────────────┐            │
│  │ app          │            │
│  │ FastAPI      │            │
│  │ 포트 8000     │            │
│  └──────┬───────┘            │
│         │ db:5432            │
│         ▼                    │
│  ┌──────────────┐            │
│  │ db           │            │
│  │ PostgreSQL   │            │
│  │ 포트 5432     │            │
│  └──────┬───────┘            │
└─────────┼────────────────────┘
          ▼
   PostgreSQL Volume
   데이터 영구 보관
```
* app 컨테이너는 FastAPI를 실행한다.
* db 컨테이너는 PostgreSQL을 실행한다. 
* 두 컨테이너는 Docker Network를 통해 통신한다. 
* PostgreSQL 데이터는 Volume에 저장한다. 
* Docker Compose가 두 컨테이너를 한꺼번에 관리한다.

## 실행 및 확인
### 도커 실행 
```
docker compose up --build
```
### Volume 확인
```
docker compose down
docker compose up
```
=> 숫자가 이어지면 Volume 유지된것.
### 로그 & 접속 확인
```
# 앱 로그
docker compose logs app

# DB 로그
docker compose logs db

# app 컨테이너 내부
docker compose exec app sh

# PostgreSQL 접속
docker compose exec db psql -U appuser -d appdb
```