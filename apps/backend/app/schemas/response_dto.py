# apps/backend/app/schemas/response_dto.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- 공통 ---
class SentimentRatio(BaseModel):
    positive: float
    negative: float
    neutral: float

class CompanyItem(BaseModel):
    company_id: int
    name_ko: str

# --- 리포트 ---
class ReportSummaryResponse(BaseModel):
    company_name: str
    sentiment_ratio: SentimentRatio
    positive_points: List[str]
    risk_factors: List[str]

class NewsSimpleItem(BaseModel):
    article_id: int
    title: str
    one_line_summary: str
    source: str
    published_at: datetime

class KeywordGroup(BaseModel):
    keyword: str
    news_items: List[NewsSimpleItem]

class ReportNewsResponse(BaseModel):
    keyword_groups: List[KeywordGroup]

# --- 뉴스 상세 ---
class NewsDetailResponse(BaseModel):
    article_id: int
    title: str
    source: str
    published_at: datetime
    key_summary: str
    original_link: str