# Backend API (FastAPI)

FastAPI 기반 백엔드 서비스입니다. **파이썬이 처음인 팀원도** 아래 순서대로 그대로 하면 로컬 실행까지 완료됩니다.

---

## 0) 사전 준비

### A. Python
- 팀 합의 버전: **3.13** (없다면 설치 필요)
  - Windows: Microsoft Store / 공식 인스톨러
  - macOS/Linux: 권장 `pyenv` (선택)

### B. Poetry (패키지/가상환경 관리자)
- **Windows (PowerShell)**:
  
  **Poetry 설치**
  ```powershell
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
  ```
  **실행 중이던 powershell 종료 후 새 창 켜서 시작**
  ```
  $poetryBin = "C:\Users\YOOJIIN\AppData\Roaming\Python\Scripts"
  $userPath  = [Environment]::GetEnvironmentVariable("Path","User")
  if ($userPath -notlike "*$poetryBin*") {
    [Environment]::SetEnvironmentVariable("Path", $userPath + ";" + $poetryBin, "User")
  }
  ```
  **설치 확인**
  ```
  poetry --version
  ```

## 1) 레포 클론 & 디렉터리 이동
```
git clone <REPO_URL> insightBee
```
```
cd insightBee/apps/backend-api
```
## 2) 가상환경 생성 & 의존성 설치
```
poetry config virtualenvs.in-project true
```
```
poetry env use 3.13          # 팀 합의 버전(예: 3.13)
```
```
poetry install               # 의존성 패키지 설치
```

## 3) 서버 실행
```
poetry run uvicorn app.main:app --reload
```

