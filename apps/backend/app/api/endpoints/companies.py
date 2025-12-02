from fastapi import APIRouter, Depends, Query
from typing import List
from google.cloud import bigquery

from app.schemas.response_dto import CompanyItem
from app.api.deps import get_bq_client, PROJECT_ID, DATASET_ID, COMBINED_TABLE_NAME

router = APIRouter()

@router.get("/companies", response_model=List[CompanyItem])
def search_companies(
    query: str = Query(..., description="검색할 기업명 (예: 삼성)"),
    client: bigquery.Client = Depends(get_bq_client)
):
    # 뷰 테이블 사용
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{COMBINED_TABLE_NAME}"

    sql = f"""
        SELECT DISTINCT search_keyword as name_ko
        FROM `{table_id}`
        WHERE search_keyword LIKE @query_pattern
        LIMIT 10
    """
    
    # SQL 파라미터 바인딩 (SQL Injection 방지)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("query_pattern", "STRING", f"%{query}%")
        ]
    )

    query_job = client.query(sql, job_config=job_config)
    results = query_job.result()

    
    return [
        CompanyItem(company_id=abs(hash(row.name_ko)) % 100000, name_ko=row.name_ko) 
        for row in results if row.name_ko
    ]