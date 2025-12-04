from dotenv import load_dotenv
import os

# 1. [필수] 앱 시작 전 환경변수(.env) 로드
# DB 접속 정보 등을 config.py가 읽기 전에 메모리에 올려야 에러가 안 납니다.
load_dotenv()

from fastapi import FastAPI
from app.api.api_router import api_router
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="InsightBee API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://insightbee-frontend-950949202751.europe-west1.run.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # 허용할 도메인
    allow_credentials=True,
    allow_methods=["*"],      # GET, POST 등 모든 메서드 허용
    allow_headers=["*"],      # 모든 헤더 허용
)

# 2. 통합된 라우터 등록
# 모든 API 주소 앞에 자동으로 '/api' 접두사가 붙습니다.
# 예: /companies -> /api/companies
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    """서버 상태 확인용 기본 루트 API"""
    return {"message": "InsightBee API Server Running (Modularized)"}
