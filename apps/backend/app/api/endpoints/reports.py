from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.schemas import response_dto
from app.api.deps import get_db, parse_keywords
from apps.dataflow.common.models import Companies, NewsArticle
from datetime import datetime

router = APIRouter()

@router.get("/report/summary", response_model=response_dto.ReportSummaryResponse)
async def get_report_summary(company_name: str, session: AsyncSession = Depends(get_db)):
    # 1. 회사 조회
    stmt_co = select(Companies).where(Companies.name_ko == company_name)
    company = (await session.execute(stmt_co)).scalars().first()
    if not company: raise HTTPException(404, "Company not found")

    # 2. 뉴스 조회 (최근 100개)
    stmt_news = select(NewsArticle).where(NewsArticle.company_id == company.id).limit(100)
    articles = (await session.execute(stmt_news)).scalars().all()

    # 3. 비율 계산 (Service 로직이 여기 들어감, 복잡해지면 crud/ 폴더로 이동 추천)
    total = len(articles)
    ratio = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    if total > 0:
        pos = sum(1 for a in articles if a.score > 0)
        neg = sum(1 for a in articles if a.score < 0)
        ratio = {
            "positive": round(pos / total, 2),
            "negative": round(neg / total, 2),
            "neutral": round((total - pos - neg) / total, 2)
        }

    return response_dto.ReportSummaryResponse(
        company_name=company.name_ko,
        sentiment_ratio=response_dto.SentimentRatio(**ratio),
        positive_points=["DB/AI 연동 전 임시 데이터"],
        risk_factors=["DB/AI 연동 전 임시 데이터"]
    )

@router.get("/report/news", response_model=response_dto.ReportNewsResponse)
async def get_report_news(
    company_name: str,
    sentiment: str = Query(None),
    sort_order: str = Query("latest"),
    session: AsyncSession = Depends(get_db)
):
    # (생략: 이전 코드와 동일한 로직, 파일만 분리됨)
    return response_dto.ReportNewsResponse(keyword_groups=[])