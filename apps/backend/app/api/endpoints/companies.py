from fastapi import APIRouter, Depends, Query
from typing import List
from google.cloud import bigquery

from app.schemas.response_dto import CompanyItem
from app.api.deps import get_bq_client, PROJECT_ID, DATASET_ID
from app.api.deps import get_bq_client, PROJECT_ID, DATASET_ID, RAW_TABLE_NAME

router = APIRouter()

@router.get("/companies", response_model=List[CompanyItem])
def search_companies(
    query: str = Query(..., description="검색할 기업명 (예: 삼성)"),
    client: bigquery.Client = Depends(get_bq_client)
):
    """
    [기업 검색 API]
    사용자가 입력한 검색어(query)가 포함된 회사 이름을 반환합니다.
    회사 목록 테이블이 따로 없으므로, _raw 테이블의 'search_keyword'를 뒤져서 찾습니다.
    """
    #원본 데이터 테이블
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{RAW_TABLE_NAME}"

    # search_keyword 컬럼을 name_ko별칭으로 가져옴
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

    #결과 반환 company_id는 임시로 해시값 사용
    return [
        CompanyItem(company_id=abs(hash(row.name_ko)) % 100000, name_ko=row.name_ko) 
        for row in results if row.name_ko
    ]