from fastapi import APIRouter, Depends
from google.cloud import bigquery
from datetime import datetime, timedelta
from collections import Counter

from app.schemas import response_dto
# deps.py에 REPORT_TABLE_NAME이 꼭 추가되어 있어야 합니다.
from app.api.deps import get_bq_client, PROJECT_ID, DATASET_ID, REPORT_TABLE_NAME

router = APIRouter()

# --------------------------------------------------------------------------
# 1. 핵심 포인트 API (주간 리포트 기반)
# URL: /api/analytics/points
# --------------------------------------------------------------------------
@router.get("/points", response_model=response_dto.CorePointsResponse)
def get_core_points(
    company_name: str,
    client: bigquery.Client = Depends(get_bq_client)
):
    """
    [트렌드 분석] 오늘 기준 최근 7일(1주) 내에 발행된 모든 주간 리포트를 조회하여 긍정/리스크 요인을 반환합니다.
    """
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{REPORT_TABLE_NAME}"
    # 최근 7일(1주) 전 날짜 계산
    one_week_ago = datetime.now() - timedelta(days=7)

    sql = f"""
        SELECT 
            report_end_date, 
            positive_points, 
            risk_factors
        FROM `{table_id}`
        WHERE company_name = @company_name
          AND report_end_date >= @start_date
        ORDER BY report_end_date DESC
        LIMIT 1
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name),
            # BigQuery DATE/TIMESTAMP 비교를 위해 파이썬 timestamp 객체 전달
            bigquery.ScalarQueryParameter("start_date", "DATE", one_week_ago.date())
        ]
    )
    
    rows = list(client.query(sql, job_config=job_config).result())
    
    points = []
    
    for report in rows:
        report_date = report.report_end_date
        
        # 1) 긍정 요인 파싱
        if report.positive_points:
            # DB 저장 형태(List vs String) 확인
            if isinstance(report.positive_points, list):
                p_list = report.positive_points
            else:
                p_list = str(report.positive_points).split('\n')
            
            for p in p_list:
                clean_p = p.strip()
                # 마크다운 기호 제거
                if clean_p.startswith('- '): clean_p = clean_p[2:]
                elif clean_p.startswith('* '): clean_p = clean_p[2:]
                
                if clean_p:
                    points.append(response_dto.CorePointItem(
                        date=report_date,
                        summary=f"[긍정] {clean_p}"
                    ))
        
        # 2) 리스크 요인 파싱
        if report.risk_factors:
            if isinstance(report.risk_factors, list):
                r_list = report.risk_factors
            else:
                r_list = str(report.risk_factors).split('\n')
            
            for r in r_list:
                clean_r = r.strip()
                if clean_r.startswith('- '): clean_r = clean_r[2:]
                elif clean_r.startswith('* '): clean_r = clean_r[2:]
                
                if clean_r:
                    points.append(response_dto.CorePointItem(
                        date=report_date,
                        summary=f"[리스크] {clean_r}"
                    ))

    return response_dto.CorePointsResponse(
        company_name=company_name,
        points=points
    )

# --------------------------------------------------------------------------
# 2. 핵심 키워드 API (주간 리포트 기반)
# URL: /api/analytics/keywords
# --------------------------------------------------------------------------
@router.get("/keywords", response_model=response_dto.CoreKeywordsResponse)
def get_core_keywords(
    company_name: str,
    client: bigquery.Client = Depends(get_bq_client)
):
    """
    [트렌드 분석] 최근 7일(1주) 내 리포트에서 키워드를 추출하고, 많이 등장한 순서대로 반환합니다.
    """
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{REPORT_TABLE_NAME}"
    one_week_ago = datetime.now() - timedelta(days=7)
    
    #날짜 조건 추가
    sql = f"""
        SELECT keywords, report_end_date
        FROM `{table_id}`
        WHERE company_name = @company_name
          AND report_end_date >= @start_date
        ORDER BY report_end_date DESC
        LIMIT 1
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("company_name", "STRING", company_name),
            bigquery.ScalarQueryParameter("start_date", "DATE", one_week_ago.date())
        ]
    )
    
    rows = list(client.query(sql, job_config=job_config).result())
    
    
    keyword_items = []
    
    for report in rows:
        if report.keywords:
            k_list = []
            if isinstance(report.keywords, list):
                k_list = report.keywords
            else:
                raw_str = str(report.keywords).replace('[','').replace(']','').replace("'", "").replace('"', "")
                k_list = raw_str.split(',')
            
            for k in k_list:
                clean_k = k.strip()
                if clean_k:
                    # 중복 제거 없이 있는 그대로 다 넣거나, 
                    # 중복만 제거하고 싶다면 Set을 썼다가 List로 변환하면 됩니다.
                    # 여기서는 요청대로 "리스트로 쭉쭉쭉 던져주는" 방식 (중복 허용 여부에 따라 조정 가능)
                    keyword_items.append(response_dto.CoreKeywordItem(
                        keyword=clean_k
                    ))
    
    return response_dto.CoreKeywordsResponse(
        company_name=company_name,
        keywords=keyword_items
    )