from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import bigquery
from typing import List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse

from app.schemas import response_dto
from app.api.deps import get_bq_client, PROJECT_ID, DATASET_ID, COMBINED_TABLE_NAME

router = APIRouter()

@router.get("/report/summary", response_model=response_dto.ReportSummaryResponse)
def get_report_summary(
    company_name: str,
    client: bigquery.Client = Depends(get_bq_client)
):
    # 뷰 테이블 사용
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{COMBINED_TABLE_NAME}"
    
    # ---------------------------------------------------------
    # 1. [추가된 로직] 최근 3개월 기사 개수 별도 조회
    # ---------------------------------------------------------
    three_months_ago = datetime.now() - timedelta(days=90)
    
    count_sql = f"""
        SELECT COUNT(*) as total_count
        FROM `{table_id}`
        WHERE search_keyword = @company_name
        AND published_at >= @start_date
    """
    
    count_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name),
            # BigQuery의 DATETIME/TIMESTAMP 타입에 맞춰 파이썬 timestamp 객체를 넘김
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", three_months_ago) 
        ]
    )
    
    # 개수 조회 실행
    count_result = list(client.query(count_sql, job_config=count_job_config).result())
    real_total_count = count_result[0].total_count if count_result else 0

    # ---------------------------------------------------------
    # 2. 리포트 분석용 데이터 조회
    # ---------------------------------------------------------
    
    sql = f"""
        SELECT 
            article_id, 
            title, 
            sentiment, 
            one_sentence_summary
        FROM `{table_id}`
        WHERE search_keyword = @company_name
        ORDER BY published_at DESC
        LIMIT 2000
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name)
        ]
    )
    
    rows = list(client.query(sql, job_config=job_config).result())
    
    if not rows:
        raise HTTPException(404, "해당 기업의 분석 데이터를 찾을 수 없습니다.")

    # ---------------------------------------------------------
    # 3. 긍/부정 비율 및 요약 추출
    # ---------------------------------------------------------
    fetched_count = len(rows)
    pos = 0
    neg = 0
    
    for r in rows:
        if not r.sentiment: continue
        s = r.sentiment.lower()
        if "positive" in s or "긍정" in s: pos += 1
        elif "negative" in s or "부정" in s: neg += 1
            
    neu = fetched_count - (pos + neg)
    
    ratio = response_dto.SentimentRatio(
        positive=round(pos/fetched_count, 2) if fetched_count else 0,
        negative=round(neg/fetched_count, 2) if fetched_count else 0,
        neutral=round(neu/fetched_count, 2) if fetched_count else 0
    )

    def is_positive(text): return text and ("positive" in text.lower() or "긍정" in text)
    def is_negative(text): return text and ("negative" in text.lower() or "부정" in text)

    pos_points = [r.one_sentence_summary or r.title for r in rows if is_positive(r.sentiment)][:3]
    neg_points = [r.one_sentence_summary or r.title for r in rows if is_negative(r.sentiment)][:3]
    
    if not pos_points: pos_points = [r.title for r in rows if is_positive(r.sentiment)][:3]
    if not neg_points: neg_points = [r.title for r in rows if is_negative(r.sentiment)][:3]

    return response_dto.ReportSummaryResponse(
        company_name=company_name,
        total_article_count=real_total_count,  # 3개월치 카운트 반환
        sentiment_ratio=ratio,
        positive_points=pos_points if pos_points else ["긍정적인 주요 이슈가 없습니다."],
        risk_factors=neg_points if neg_points else ["부정적인 주요 리스크가 없습니다."]
    )

@router.get("/report/news", response_model=response_dto.ReportNewsResponse)
def get_report_news_list(
    company_name: str,
    sentiment: Optional[str] = Query(None),
    sort_order: str = "newest",
    client: bigquery.Client = Depends(get_bq_client)
):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{COMBINED_TABLE_NAME}"
    
    sql = f"""
        SELECT 
            article_id, 
            title, 
            published_at, 
            url,
            sentiment, 
            topic, 
            one_sentence_summary
        FROM `{table_id}`
        WHERE search_keyword = @company_name
    """
    
    if sentiment == "positive":
        sql += " AND (LOWER(sentiment) LIKE '%positive%' OR sentiment LIKE '%긍정%')"
    elif sentiment == "negative":
        sql += " AND (LOWER(sentiment) LIKE '%negative%' OR sentiment LIKE '%부정%')"
        
    
    if sort_order == "oldest":
        sql += " ORDER BY published_at ASC NULLS LAST"
    else:
        sql += " ORDER BY published_at DESC NULLS LAST"
        
    sql += " LIMIT 2000"

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name)
        ]
    )

    rows = list(client.query(sql, job_config=job_config).result())

    groups = {}
    for row in rows:
        main_kwd = row.topic if row.topic else "기타"
        
        source_name = "언론사"
        if row.url:
            try:
                parsed = urlparse(row.url)
                source_name = parsed.netloc.replace("www.", "")
            except:
                pass

        if main_kwd not in groups:
            groups[main_kwd] = []
            
        groups[main_kwd].append(response_dto.NewsSimpleItem(
            article_id=row.article_id,
            title=row.title,
            one_line_summary=row.one_sentence_summary if row.one_sentence_summary else row.title,
            source=source_name,
            sentiment=row.sentiment if row.sentiment else "중립",
            # 날짜 없으면 현재 시간으로 채움 (Swagger/프론트 오류 방지)
            published_at=row.published_at if row.published_at else datetime.now()
        ))
    
    result_groups = [
        response_dto.KeywordGroup(keyword=k, news_items=v)
        for k, v in groups.items()
    ]
    
    return response_dto.ReportNewsResponse(
        keyword_groups=result_groups
    )