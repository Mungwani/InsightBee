from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.response_dto import CompanyItem
from app.api.deps import get_db
from apps.dataflow.common.models import Companies

router = APIRouter()

@router.get("/companies", response_model=List[CompanyItem])
async def search_companies(
    query: str = Query(..., description="검색할 기업명"),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Companies).where(Companies.name_ko.like(f"%{query}%")).limit(10)
    result = await session.execute(stmt)
    return [CompanyItem(company_id=c.id, name_ko=c.name_ko) for c in result.scalars().all()]