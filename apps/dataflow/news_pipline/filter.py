# apps/dataflow/news_pipeline/filter.py
import logging
from typing import Dict, Any

# 이 필터 모듈이 사용할 규칙 파일들을 임포트
from . import keywords       # 2단계: 키워드별 점수 정의 (e.g., "채용": 15점)
from . import filter_rules   # 1단계: 회사별 제외 키워드 정의 (e.g., "KT" -> "KT&G" 제외)

def filter_and_score_article(scraped_article: Dict[str, Any]) -> Dict[str, Any]:
    """
    [동기] 스크래핑된 기사 1건을 받아, 비즈니스 로직(규칙)에 따라
    통과(Passed)/실패(Failed) 여부와 점수(Score)를 반환합니다.
    
    [입력] scraped_article: 
        { 'title': '...', 'content': '...', 'search_keyword': '회사명', ... }
        
    [출력] 
        { 'passed': True/False, 'score': 15, 'matched_keywords': "[('채용', 15)]" }
    """
    
    # --- [데이터 준비] ---
    # 스크래핑에 실패한 경우를 대비해 .get()으로 안전하게 데이터 추출
    title = scraped_article.get('title', '')
    content = scraped_article.get('content', '') 
    company_name = scraped_article.get('search_keyword', '') # e.g., "KT", "삼성전자"
    
    # --- 1단계: 명시적 제외 필터링 (제목만 검사) ---
    # (filter_rules.py)
    # e.g., "KT"로 검색 시, "KT&G", "KT알파" 등 계열사/무관 기사 제외
    
    # filter_rules.COMPANY_EXCLUSION_RULES 딕셔너리에서 현재 회사명의 제외 키워드 리스트를 가져옴
    exclusion_list = filter_rules.COMPANY_EXCLUSION_RULES.get(company_name, [])
    
    for exclusion_keyword in exclusion_list:
        # 기사 제목(소문자)에 제외 키워드(소문자)가 포함되어 있다면,
        if exclusion_keyword.lower() in title.lower():
            # 즉시 "실패" 처리하고 함수 종료
            logging.debug(f"[Filtered-Rule] '{title}' (contains: {exclusion_keyword})")
            return {
                "passed": False, 
                "score": 0,
                "matched_keywords": f"ExclusionRule: {exclusion_keyword}" # 탈락 사유
            }

    # --- 2단계: 관련성 스코어링 (제목 + 본문 검사) ---
    # (keywords.py)
    # "채용", "실적" 등 긍정 키워드와 "부고", "스포츠" 등 부정 키워드를 기반으로 점수 합산
    
    # 검색 효율을 위해 제목과 본문을 합치고 모두 소문자로 변경
    content_for_scoring = f"{title} {content}".lower() 
    score = 0; matched_keywords = []

    # keywords.ALL_KEYWORDS 딕셔너리 (e.g., {"채용": 15, "부고": -999}) 순회
    for keyword, value in keywords.ALL_KEYWORDS.items():
        # 합쳐진 텍스트에 키워드가 포함되어 있다면,
        if keyword.lower() in content_for_scoring:
            score += value # 점수 합산
            matched_keywords.append((keyword, value)) # 매칭된 키워드 기록
            
            # [즉시 탈락] 만약 점수가 -999 이하 (IRRELEVANT_KEYWORDS)라면,
            # 더 계산할 필요 없이 즉시 "실패" 처리하고 함수 종료
            if value <= -999:
                logging.debug(f"[Filtered-Irrelevant] '{title}' (contains: {keyword})")
                return {
                    "passed": False, 
                    "score": value, # (e.g., -999)
                    "matched_keywords": str(matched_keywords)
                } 

    # --- 3단계: 최종 임계값(Threshold) 검사 ---
    # (keywords.py의 PASS_THRESHOLD 값과 비교)
    # e.g., PASS_THRESHOLD = 10
    
    # 2단계에서 합산된 총 점수가 임계값(e.g., 10점)보다 낮으면 "실패" 처리
    if score < keywords.PASS_THRESHOLD:
        logging.debug(f"[Filtered-LowScore] Score {score} < {keywords.PASS_THRESHOLD} for '{title}'")
        return {
            "passed": False, 
            "score": score,
            "matched_keywords": str(matched_keywords)
        }

    # --- 4단계: 최종 통과 ---
    # 1, 2, 3단계를 모두 통과한 기사
    logging.info(f"[PASSED] Score {score} for '{title}'")
    return {
        "passed": True, 
        "score": score,
        "matched_keywords": str(matched_keywords)
    }