from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ==========================================
# [공통 사용 모델]
# ==========================================

class SentimentRatio(BaseModel):
    """
    뉴스 기사들의 긍정/부정/중립 비율을 나타냅니다.
    값은 0.0 ~ 1.0 사이의 실수(float)
    """
    positive: float
    negative: float
    neutral: float

class CompanyItem(BaseModel):
    """
    기업 검색 결과 항목
    """
    company_id: int
    name_ko: str

# ==========================================
# [API별 응답(Response) 모델]
# ==========================================

# --- 1. 리포트 페이지용 ---

class ReportSummaryResponse(BaseModel):
    """
    리포트 상단 : 요약 정보 및 통계
    """
    company_name: str
    total_article_count : int # 최근 3개월 기사 총 개수
    sentiment_ratio: SentimentRatio # 위에서 정의한 SentimentRatio 모델 재사용
    positive_points: List[str]      # 긍정 요약 문장
    risk_factors: List[str]         # 부정 요약 문장

class NewsSimpleItem(BaseModel):
    """
    뉴스 리스트 아이템
    """
    article_id: int
    title: str
    one_line_summary: str      
    source: str                # 언론사 이름
    published_at: Optional[datetime]     # 발행일(날짜 없을 경우 -> null)

class KeywordGroup(BaseModel):
    """
    특정 키워드로 묶인 뉴스 기사 그룹입니다.
    """
    keyword: str
    news_items: List[NewsSimpleItem]

class ReportNewsResponse(BaseModel):
    """
    리포트 하단 : 뉴스 목록 전체
    """
    keyword_groups: List[KeywordGroup]

# --- 2. 뉴스 상세 페이지용 ---

class NewsDetailResponse(BaseModel):
    """
    [뉴스 상세 페이지]
    """
    article_id: int
    title: str
    source: str
    published_at: Optional[datetime]
    key_summary: str           # 기사 핵심 내용 요약
    ai_summary : Optional[str]
    original_link: str         # 원본 링크