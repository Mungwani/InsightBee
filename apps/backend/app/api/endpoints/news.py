from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.schemas.response_dto import NewsDetailResponse
from app.api.deps import get_db
from apps.dataflow.common.models import NewsArticle

router = APIRouter()

@router.get("/news/{article_id}", response_model=NewsDetailResponse)
async def get_news_detail(
    article_id: int,
    session: AsyncSession = Depends(get_db)
):
    """
    [뉴스 상세] 특정 뉴스 ID(article_id)의 상세 정보를 반환합니다.
    """
    # PK(Primary Key)로 기사 1건 조회
    stmt = select(NewsArticle).where(NewsArticle.article_id == article_id)
    article = (await session.execute(stmt)).scalars().first()
    
    if not article:
        raise HTTPException(404, "해당 뉴스를 찾을 수 없습니다.")

    # [임시 로직] AI 요약 컬럼이 없으므로, 본문 앞부분을 요약으로 사용
    summary_text = article.content[:200] + "..." if article.content else "본문 내용 없음"

    return NewsDetailResponse(
        article_id=article.article_id,
        title=article.title,
        source="언론사",
        published_at=article.published_at or datetime.now(),
        key_summary=summary_text,
        original_link=article.url
    )