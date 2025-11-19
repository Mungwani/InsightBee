# DB 세션을 가져오는 공통 함수.
import ast
from typing import List
from apps.dataflow.common.db_sa import get_db_session

# Controller에서 'Depends(get_db)'로 사용
get_db = get_db_session

def parse_keywords(keyword_str: str) -> List[str]:
    """DB에 저장된 문자열 형태의 키워드를 리스트로 변환"""
    try:
        if not keyword_str: return []
        data = ast.literal_eval(keyword_str)
        return [k for k, v in data] if isinstance(data, list) else []
    except:
        return []