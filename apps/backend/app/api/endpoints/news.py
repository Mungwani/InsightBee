from fastapi import APIRouter, Depends, HTTPException
from google.cloud import bigquery
from datetime import datetime
from urllib.parse import urlparse

from app.schemas.response_dto import NewsDetailResponse
from app.api.deps import (
    get_bq_client, PROJECT_ID, DATASET_ID, 
    RAW_TABLE_NAME, LLM_TABLE_NAME # 추가됨
)

router = APIRouter()



@router.get("/news/{article_id}", response_model=NewsDetailResponse)
def get_news_detail(
    article_id: int,
    client: bigquery.Client = Depends(get_bq_client)
):  
    """
    뉴스 상세 조회 API : 기사 ID로 본문과 분석 결과(인사이트, 요약) 모두 조회.
    """
    raw_id = f"{PROJECT_ID}.{DATASET_ID}.{RAW_TABLE_NAME}"
    llm_id = f"{PROJECT_ID}.{DATASET_ID}.{LLM_TABLE_NAME}"
    
    # [JOIN] 상세 정보 조회
    sql = f"""
        SELECT 
            r.article_id, 
            r.title, 
            r.content, 
            r.published_at, 
            r.url,
            l.summary,
            l.career_insight
        FROM `{raw_id}` as r
        JOIN `{llm_id}` as l ON r.article_id = l.article_id
        WHERE r.article_id = @article_id
        LIMIT 1
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("article_id", "INT64", article_id)
        ]
    )
    
    rows = list(client.query(sql, job_config=job_config).result())
    
    if not rows:
        raise HTTPException(404, "해당 뉴스를 찾을 수 없습니다.")
        
    article = rows[0]
    
    #URL 파싱
    source_name = "언론사"
    if article.url:
        try:
            source_name = urlparse(article.url).netloc.replace("www.", "")
        except:
            pass
    
    # 요약 우선 순위 : 테이블 요약 -> 커리어 인사이트 -> 본문 앞부분
    final_summary = "요약 없음"
    if article.summary:
        final_summary = article.summary
    elif article.career_insight:
        final_summary = f"[커리어 인사이트]\n{article.career_insight}"
    elif article.content:
        final_summary = article.content[:300] + "..."

    return NewsDetailResponse(
        article_id=article.article_id,
        title=article.title,
        source=source_name,
        published_at=article.published_at,
        key_summary=final_summary,
        original_link=article.url
    )