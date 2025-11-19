from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.schemas.response_dto import NewsDetailResponse
from app.api.deps import get_db
from apps.dataflow.common.models import NewsArticle

router = APIRouter()

@router.get("/news/{article_id}", response_model=NewsDetailResponse)
async def get_news_detail(article_id: int, session: AsyncSession = Depends(get_db)):
    stmt = select(NewsArticle).where(NewsArticle.article_id == article_id)
    article = (await session.execute(stmt)).scalars().first()
    
    if not article: raise HTTPException(404, "Article not found")

    return NewsDetailResponse(
        article_id=article.article_id,
        title=article.title,
        source="언론사",
        published_at=article.published_at or datetime.now(),
        key_summary=article.content[:200] if article.content else "",
        original_link=article.url
    )