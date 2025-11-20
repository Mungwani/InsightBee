import ast
from typing import List
from apps.dataflow.common.db_sa import get_db_session

# [DB 세션 의존성]
# Controller에서 'Depends(get_db)'로 호출하면,
# 자동으로 DB 커넥션을 하나 꺼내주고, 요청이 끝나면 닫아줍니다.
get_db = get_db_session

def parse_keywords(keyword_str: str) -> List[str]:
    """
    [유틸리티 함수]
    DB에 저장된 키워드 문자열은 "[('키워드', 10), ...]" 형태의 텍스트입니다.
    이것을 파이썬 리스트 ['키워드', ...] 형태로 예쁘게 변환해줍니다.
    
    Args:
        keyword_str (str): DB에서 꺼낸 raw string
        
    Returns:
        List[str]: 파싱된 키워드 리스트 (실패 시 빈 리스트 반환)
    """
    try:
        if not keyword_str: return []
        # 문자열로 된 리스트 표현식을 실제 파이썬 객체로 안전하게 변환
        data = ast.literal_eval(keyword_str) 
        # 튜플 (키워드, 빈도수) 중 키워드만 추출
        return [k for k, v in data] if isinstance(data, list) else []
    except:
        return []