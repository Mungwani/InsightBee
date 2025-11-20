from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.response_dto import CompanyItem # 응답 모델
from app.api.deps import get_db                  # DB 도구
from apps.dataflow.common.models import Companies # DB 테이블

router = APIRouter()

@router.get("/companies", response_model=List[CompanyItem])
async def search_companies(
    query: str = Query(..., description="검색할 기업명 (예: 삼성)"),
    session: AsyncSession = Depends(get_db) # DB 세션 주입
):
    """
    기업명 검색 API (자동완성용)
    입력받은 query가 포함된 기업 목록을 최대 10개 반환합니다.
    """
    # SQL: SELECT * FROM companies WHERE name_ko LIKE '%query%' LIMIT 10
    stmt = select(Companies).where(Companies.name_ko.like(f"%{query}%")).limit(10)
    result = await session.execute(stmt)
    
    # DB 모델(Companies)을 Pydantic 모델(CompanyItem)로 변환하여 반환
    return [CompanyItem(company_id=c.id, name_ko=c.name_ko) for c in result.scalars().all()]