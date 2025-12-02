from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import bigquery
from typing import List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse

from app.schemas import response_dto

from app.api.deps import (
    get_bq_client, PROJECT_ID, DATASET_ID, 
    RAW_TABLE_NAME, LLM_TABLE_NAME
)

router = APIRouter()


@router.get("/report/summary", response_model=response_dto.ReportSummaryResponse)
def get_report_summary(
    company_name: str,
    client: bigquery.Client = Depends(get_bq_client)
):  
    """
    리포트 상단 요약 API : 특정 기업 뉴스 긍/부정 비율+주요 요약 포인트
    """
    raw_id = f"{PROJECT_ID}.{DATASET_ID}.{RAW_TABLE_NAME}"
    llm_id = f"{PROJECT_ID}.{DATASET_ID}.{LLM_TABLE_NAME}"

    # 해당 기업 최근 3개월 기사 총 개수 구하기
    three_months_ago = datetime.now() - timedelta(days=90)
    
    count_sql = f"""
        SELECT COUNT(*) as total_count
        FROM `{raw_id}`
        WHERE search_keyword = @company_name
        AND published_at >= @start_date
    """
    
    count_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name),
            bigquery.ScalarQueryParameter("start_date", "DATETIME", three_months_ago) # DB 타입에 따라 TIMESTAMP로 변경 필요할 수 있음
        ]
    )
    
    count_result = list(client.query(count_sql, job_config=count_job_config).result())
    real_total_count = count_result[0].get("total_count", 0) if count_result else 0
    
    # article_id기준으로 합쳐서 필요한 정보만 가져옴.
    sql = f"""
        SELECT 
            r.article_id, 
            r.title, 
            l.sentiment, 
            l.one_sentence_summary
        FROM `{raw_id}` as r
        JOIN `{llm_id}` as l ON r.article_id = l.article_id
        WHERE r.search_keyword = @company_name
        ORDER BY r.published_at DESC
        LIMIT 100
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name)
        ]
    )
    
    # 쿼리 실행 및 결과 리스트 반환
    rows = list(client.query(sql, job_config=job_config).result())
    
    if not rows:
        raise HTTPException(404, "해당 기업의 분석 데이터를 찾을 수 없습니다.")

    # 점수 계산 대신 글자('긍정', '부정')를 직접 셉니다.
    total = len(rows)
    pos = 0
    neg = 0
    
    for r in rows:
        # 1. 값이 없으면 스킵
        if not r.sentiment:
            continue
            
        # 2. 소문자로 바꿔서 비교 (대소문자 무시)
        s = r.sentiment.lower()
        
        # 3. 'positive' 또는 '긍정'이 포함되어 있으면 카운트
        if "positive" in s or "긍정" in s:
            pos += 1
        # 4. 'negative' 또는 '부정'이 포함되어 있으면 카운트
        elif "negative" in s or "부정" in s:
            neg += 1
            
    neu = total - (pos + neg)
    
    ratio = response_dto.SentimentRatio(
        positive=round(pos/total, 2) if total else 0,
        negative=round(neg/total, 2) if total else 0,
        neutral=round(neu/total, 2) if total else 0
    )

    # 요약 포인트 
    def is_positive(text):
        if not text: return False
        t = text.lower()
        return "positive" in t or "긍정" in t

    def is_negative(text):
        if not text: return False
        t = text.lower()
        return "negative" in t or "부정" in t

    pos_points = [r.one_sentence_summary or r.title for r in rows if is_positive(r.sentiment)][:3]
    neg_points = [r.one_sentence_summary or r.title for r in rows if is_negative(r.sentiment)][:3]
    
    # 요약 없으면 제목으로 대체
    if not pos_points:
        pos_points = [r.title for r in rows if is_positive(r.sentiment)][:3]
    if not neg_points:
        neg_points = [r.title for r in rows if is_negative(r.sentiment)][:3]

    return response_dto.ReportSummaryResponse(
        company_name=company_name,
        sentiment_ratio=ratio,
        positive_points=pos_points if pos_points else ["긍정적인 주요 이슈가 없습니다."],
        risk_factors=neg_points if neg_points else ["부정적인 주요 리스크가 없습니다."]
    )

@router.get("/report/news", response_model=response_dto.ReportNewsResponse)
def get_report_news_list(
    company_name: str,
    sentiment: Optional[str] = Query(None, description="'positive' 또는 'negative'"),
    sort_order: str = "newest",
    client: bigquery.Client = Depends(get_bq_client)
):  
    """
    뉴스 리스트 API : 필터링(긍/부정) 및 정렬 기능을 포함한 뉴스 목록 반환.
    """
    raw_id = f"{PROJECT_ID}.{DATASET_ID}.{RAW_TABLE_NAME}"
    llm_id = f"{PROJECT_ID}.{DATASET_ID}.{LLM_TABLE_NAME}"
    
    sql = f"""
        SELECT 
            r.article_id, 
            r.title, 
            r.published_at, 
            r.url,
            l.sentiment, 
            l.topic, 
            l.one_sentence_summary
        FROM `{raw_id}` as r
        JOIN `{llm_id}` as l ON r.article_id = l.article_id
        WHERE r.search_keyword = @company_name
    """
    
    if sentiment == "positive":
        sql += " AND (LOWER(l.sentiment) LIKE '%positive%' OR l.sentiment LIKE '%긍정%')"
    elif sentiment == "negative":
        sql += " AND (LOWER(l.sentiment) LIKE '%negative%' OR l.sentiment LIKE '%부정%')"
        
    if sort_order == "oldest":
        sql += " ORDER BY r.published_at ASC NULLS LAST"
    else:
        sql += " ORDER BY r.published_at DESC NULLS LAST"
        
    sql += " LIMIT 50"

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name)
        ]
    )

    rows = list(client.query(sql, job_config=job_config).result())

    #[데이터 가공] 토픽별 그룹핑 및 URL 파싱
    groups = {}
    for row in rows:
        main_kwd = row.topic if row.topic else "기타"
        
        # URL에서 도메인 추출 로직
        source_name = "언론사"
        if row.url:
            try:
                parsed = urlparse(row.url)
                source_name = parsed.netloc.replace("www.", "") # www. 제거
            except:
                pass

        if main_kwd not in groups:
            groups[main_kwd] = []
            
        groups[main_kwd].append(response_dto.NewsSimpleItem(
            article_id=row.article_id,
            title=row.title,
            one_line_summary=row.one_sentence_summary if row.one_sentence_summary else row.title,
            source=source_name,  # 추출한 도메인 사용
            published_at=row.published_at if row.published_at else datetime.now() # (None 허용은 response_dto 수정 후 문제 없음)
        ))
    
    #딕셔너리를 리스트 형태로 반환
    result_groups = [
        response_dto.KeywordGroup(keyword=k, news_items=v)
        for k, v in groups.items()
    ]
    
    return response_dto.ReportNewsResponse(
        keyword_groups=result_groups
    )
