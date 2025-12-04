import os
import ast
from typing import List, Generator, Any
from google.cloud import bigquery
from dotenv import load_dotenv

# .env 파일 로드 (파일이 없으면 시스템 환경변수 사용)
load_dotenv()

# =========================================================
# [환경 변수 로드] 뷰 테이블 하나로 통합.
# =========================================================
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BIGQUERY_DATASET_ID")
COMBINED_TABLE_NAME = os.getenv("TABLE_NEWS_COMBINED") # 뷰
REPORT_TABLE_NAME = os.getenv("TABLE_WEEKLY_REPORT")

# 필수 설정값 체크 (배포 시 실수 방지용)
if not all([PROJECT_ID, DATASET_ID, COMBINED_TABLE_NAME, REPORT_TABLE_NAME]):
    raise ValueError("필수 환경변수(.env)가 설정되지 않았습니다. GCP_PROJECT_ID 등을 확인하세요.")

def get_bq_client() -> Generator[bigquery.Client, None, None]:
    """
    [DI] 빅쿼리 클라이언트를 생성.
        1. 시작 : client 생성 + yield( API 함수에 전달)
        2. 처리 : API 함수가 이 client를 사용해 DB 조회
        3. 종료 : finally 실행 -> client.close()
    """
    client = bigquery.Client(project=PROJECT_ID)
    try:
        yield client
    finally:
        client.close()

def parse_keywords(keyword_data: Any) -> List[str]:
    """
    [유틸리티]
    빅 쿼리에 저장된 키워드 데이터가 다양한 형태(문자열, 리스트, 구조체 등)로 저장될 가능성이 있어서
    안전하게 파이썬 리스트['키워드1', '키워드2']로 반환
    """
    if not keyword_data:
        return []
    
    # Case 1: 이미 리스트(ARRAY) 형태인 경우
    if isinstance(keyword_data, list):
        # 내부가 딕셔너리(Struct)인 경우 처리
        if keyword_data and isinstance(keyword_data[0], dict):
             return [item.get('keyword', item) for item in keyword_data]
        return keyword_data

    # Case 2: 문자열("[('키워드', 10), ...]") 형태인 경우
    try:
        data = ast.literal_eval(str(keyword_data))
        # [('키워드', 10), ...] 튜플 형태라면 키워드만 추출
        if isinstance(data, list) and data and isinstance(data[0], tuple):
            return [k for k, v in data]
        return data if isinstance(data, list) else []
    except:
        return []