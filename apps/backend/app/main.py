# apps/backend/app/main.py
from dotenv import load_dotenv # [추가]
import os

# [중요] 다른 imports보다 먼저 .env를 로드해야 합니다.
# 그래야 아래 api_router -> config.py 가 실행될 때 환경변수가 채워져 있습니다.
load_dotenv()

from fastapi import FastAPI
from app.api.api_router import api_router # 이 줄이 실행될 때 config.py도 실행됨

app = FastAPI(title="InsightBee API")

# 모든 라우터 등록 (프리픽스 /api 추가)
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "InsightBee API Server Running (Modularized)"}