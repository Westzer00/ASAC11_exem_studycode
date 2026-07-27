1. 프로젝트 구조 생성
2. 가상환경 생성
3. 필요한 패키지 설치
4. pyproject.toml 작성
4. 환경변수 로딩
5. 다른 디렉터리에서 실행했을 때 발생하는 Import 오류 수정
6. .env는 제외하고 .env.example만 Git에 포함


=> tomal : 프로젝트 이름과 필요한 패캐지를 작성한 파일 
=> .env : 실제 환경변구 값 넣음 !! (현재는 api가 없어서 문자로 대체)
=> .env.example : 환경변수랑 이름만 ! 공유하는 파일 (git에 올라가는 환경 예시 파일로 제작, 여기에는 api 토큰 같은건 넣지 않음)
*** => .gitignore : .env 와 가상환경이 올라가지 않도록 분리하는 파일 ***


구조트리
```text
day02/am/
├── .venv/               # 가상환경, Git 제외
├── .env                 # 실제 환경변수, Git 제외
├── .env.example         # 환경변수 예시
├── .gitignore
├── pyproject.toml
├── README.md
└── src/
    └── day02_am/
        ├── __init__.py
        └── main.py