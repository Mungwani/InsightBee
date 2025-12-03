from fastapi import APIRouter, Depends, HTTPException
from google.cloud import bigquery
from datetime import datetime
from urllib.parse import urlparse

from app.schemas.response_dto import NewsDetailResponse
from app.api.deps import get_bq_client, PROJECT_ID, DATASET_ID, COMBINED_TABLE_NAME

router = APIRouter()



@router.get("/news/{article_id}", response_model=NewsDetailResponse)
def get_news_detail(
    article_id: int,
    client: bigquery.Client = Depends(get_bq_client)
):  
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{COMBINED_TABLE_NAME}"
    
    # [수정됨] JOIN 제거. career_insight는 없어서 뺐습니다.
    sql = f"""
        SELECT 
            article_id, 
            title, 
            content, 
            published_at, 
            url,
            summary,
            career_insight,
            sentiment
        FROM `{table_id}`
        WHERE article_id = @article_id
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
    
    # 요약 우선 순위 : career_insight 컬럼 -> summary 컬럼 -> 본문 300자(혹시 모를)
    final_summary = "요약 없음"
    
    if article.career_insight:
        final_summary = article.career_insight
    elif article.summary:
        # 요약이 너무 길 경우를 대비해 300자로 자름
        final_summary = article.summary[:300] + ("..." if len(article.summary) > 300 else "")
    elif article.content:
        final_summary = article.content[:300] + "..."

    return NewsDetailResponse(
        article_id=article.article_id,
        title=article.title,
        source=source_name,
        published_at=article.published_at,
        sentiment=article.sentiment if article.sentiment else "중립",
        key_summary=final_summary,
        ai_summary=article.summary,
        original_link=article.url
    )