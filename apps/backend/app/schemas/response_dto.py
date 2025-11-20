from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ==========================================
# [공통 사용 모델]
# 여러 API에서 재사용되는 작은 부품들입니다.
# ==========================================

class SentimentRatio(BaseModel):
    """
    뉴스 기사들의 긍정/부정/중립 비율을 나타냅니다.
    값은 0.0 ~ 1.0 사이의 실수(float)입니다.
    """
    positive: float
    negative: float
    neutral: float

class CompanyItem(BaseModel):
    """
    기업 검색 결과에 사용되는 기본 기업 정보 객체입니다.
    """
    company_id: int
    name_ko: str

# ==========================================
# [API별 응답(Response) 모델]
# 실제 API가 반환하는 최종 JSON 구조입니다.
# ==========================================

# --- 1. 리포트 페이지용 ---

class ReportSummaryResponse(BaseModel):
    """
    [리포트 페이지 상단] 
    기업 정보, 긍/부정 차트 데이터, AI 요약 포인트를 포함합니다.
    """
    company_name: str
    sentiment_ratio: SentimentRatio # 위에서 정의한 SentimentRatio 모델 재사용
    positive_points: List[str]      # AI가 분석한 긍정적 요소 (문장 리스트)
    risk_factors: List[str]         # AI가 분석한 리스크 요소 (문장 리스트)

class NewsSimpleItem(BaseModel):
    """
    리스트에 표시될 뉴스 기사 요약 정보입니다.
    """
    article_id: int
    title: str
    one_line_summary: str      # 기사 한 줄 요약 (현재는 제목 사용 중)
    source: str                # 언론사 이름
    published_at: datetime     # 발행일

class KeywordGroup(BaseModel):
    """
    특정 키워드로 묶인 뉴스 기사 그룹입니다.
    예: "AI" 키워드 그룹 -> [기사1, 기사2...]
    """
    keyword: str
    news_items: List[NewsSimpleItem]

class ReportNewsResponse(BaseModel):
    """
    [리포트 페이지 하단]
    키워드별로 그룹핑된 뉴스 목록 전체를 반환합니다.
    """
    keyword_groups: List[KeywordGroup]

# --- 2. 뉴스 상세 페이지용 ---

class NewsDetailResponse(BaseModel):
    """
    [뉴스 상세 페이지]
    기사 클릭 시 보여줄 상세 정보를 정의합니다.
    """
    article_id: int
    title: str
    source: str
    published_at: datetime
    key_summary: str           # 기사 핵심 내용 요약 (AI 또는 앞부분 발췌)
    original_link: str         # '원문 보러가기' 링크