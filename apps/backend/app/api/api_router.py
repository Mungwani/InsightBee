# apps/backend/app/api/api_router.py
from fastapi import APIRouter
from app.api.endpoints import companies, reports, news

api_router = APIRouter()

# 여기서 '/api' 프리픽스를 붙일 수도 있지만, 사용자 요청대로 직관적으로 갑니다.
api_router.include_router(companies.router, tags=["Companies"])
api_router.include_router(reports.router, tags=["Report"])
api_router.include_router(news.router, tags=["News"])