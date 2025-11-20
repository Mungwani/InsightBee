from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.schemas import response_dto
from app.api.deps import get_db, parse_keywords
from apps.dataflow.common.models import Companies, NewsArticle
from datetime import datetime

router = APIRouter()

@router.get("/report/summary", response_model=response_dto.ReportSummaryResponse)
async def get_report_summary(
    company_name: str,
    session: AsyncSession = Depends(get_db)
):
    """
    [리포트 상단] 기업의 뉴스 긍/부정 비율과 AI 요약을 반환합니다.
    """
    # 1. 기업명으로 ID 조회
    stmt_co = select(Companies).where(Companies.name_ko == company_name)
    company = (await session.execute(stmt_co)).scalars().first()
    if not company: 
        raise HTTPException(404, "해당 기업을 찾을 수 없습니다.")

    # 2. 최근 뉴스 100개 조회
    stmt_news = select(NewsArticle).where(NewsArticle.company_id == company.id).limit(100)
    articles = (await session.execute(stmt_news)).scalars().all()

    # 3. 긍/부정 비율 실시간 계산
    total = len(articles)
    ratio = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    
    if total > 0:
        pos = sum(1 for a in articles if a.score > 0) # 긍정 점수 양수
        neg = sum(1 for a in articles if a.score < 0) # 부정 점수 음수
        
        ratio = {
            "positive": round(pos / total, 2),
            "negative": round(neg / total, 2),
            "neutral": round((total - pos - neg) / total, 2)
        }

    return response_dto.ReportSummaryResponse(
        company_name=company.name_ko,
        sentiment_ratio=response_dto.SentimentRatio(**ratio),
        # [TODO] 실제 AI 요약 데이터 연동 전이므로 임시 메시지 반환
        positive_points=["최근 긍정적인 기사가 다수 포착되었습니다.", "관련 기술 투자가 활발합니다."],
        risk_factors=["글로벌 경기 변동성에 주의가 필요합니다."]
    )

@router.get("/report/news", response_model=response_dto.ReportNewsResponse)
async def get_report_news(
    company_name: str,
    sentiment: str = Query(None, description="'positive' 또는 'negative'"),
    sort_order: str = Query("latest", description="'latest'(최신순) 또는 'oldest'(오래된순)"),
    session: AsyncSession = Depends(get_db)
):
    """
    [리포트 하단] 뉴스 기사를 키워드별로 그룹핑하여 반환합니다.
    필터링(긍/부정) 및 정렬 기능을 제공합니다.
    """
    # 1. 기업 정보 조회
    stmt_co = select(Companies).where(Companies.name_ko == company_name)
    company = (await session.execute(stmt_co)).scalars().first()
    if not company: return {"keyword_groups": []}

    # 2. 기본 쿼리 생성
    query = select(NewsArticle).where(NewsArticle.company_id == company.id)

    # 3. 필터링 적용 (긍정/부정)
    if sentiment == "positive":
        query = query.where(NewsArticle.score > 0)
    elif sentiment == "negative":
        query = query.where(NewsArticle.score < 0)

    # 4. 정렬 적용
    if sort_order == "oldest":
        query = query.order_by(NewsArticle.published_at.asc())
    else:
        query = query.order_by(NewsArticle.published_at.desc())

    # 5. 데이터 실행 (최대 50개)
    articles = (await session.execute(query.limit(50))).scalars().all()

    # 6. [Python 로직] 키워드별 그룹핑
    groups = {}
    for art in articles:
        # DB의 문자열 키워드를 리스트로 변환
        keywords = parse_keywords(art.matched_keywords)
        # 첫 번째 키워드를 대표 키워드로 사용 (없으면 '기타')
        main_kwd = keywords[0] if keywords else "기타"
        
        if main_kwd not in groups:
            groups[main_kwd] = []
            
        groups[main_kwd].append(response_dto.NewsSimpleItem(
            article_id=art.article_id,
            title=art.title,
            one_line_summary=art.title, # [TODO] AI 요약 컬럼 생기면 교체
            source="언론사",
            published_at=art.published_at or datetime.now()
        ))

    # 7. 딕셔너리를 리스트 응답 모델로 변환
    keyword_groups = [
        response_dto.KeywordGroup(keyword=k, news_items=v) 
        for k, v in groups.items()
    ]
    
    return response_dto.ReportNewsResponse(keyword_groups=keyword_groups)