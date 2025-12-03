from fastapi import APIRouter
from app.api.endpoints import companies, reports, news,analytics

# 전체 API 라우터 생성
api_router = APIRouter()

# 각 파일(Controller)에서 만든 라우터를 여기에 등록합니다.
# tags: Swagger UI(/docs)에서 API를 그룹핑해서 보여줄 이름입니다.
api_router.include_router(companies.router, tags=["Companies"])
api_router.include_router(reports.router, tags=["Report"])
api_router.include_router(news.router, tags=["News"])
api_router.include_router(analytics.router,prefix="/analytics", tags=["Analytics"])