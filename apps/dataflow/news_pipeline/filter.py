import logging
import re
from typing import Dict, Any

from . import keywords
from . import filter_rules

# 1. { 'ai': ('AI', 5), 'm&a': ('M&A', 10) } 와 같은
#    소문자 키워드 -> (원본 키워드, 점수) 룩업 맵 생성
KEYWORD_MAP_LOWER = {
    k.lower(): (k, v) 
    for k, v in keywords.ALL_KEYWORDS.items()
}

# 2. 룩업 맵의 소문자 키들을 가져와서 길이가 긴 순서로 정렬
#    (e.g., 'AI 신기술'이 'AI'보다 먼저 매칭되도록 보장)
all_keyword_list_lower = sorted(KEYWORD_MAP_LOWER.keys(), key=len, reverse=True)

# 3. | (OR)로 모든 키워드를 엮은 단일 정규식 패턴 생성
#    re.escape()는 'M&A'의 '&' 같은 특수문자를 안전하게 처리
#    \b는 단어 경계를 의미 (e.g., \bai\b)
pattern_str = r'\b(' + '|'.join(re.escape(k) for k in all_keyword_list_lower) + r')\b'

# 4. 정규식을 미리 컴파일 (대소문자 무시)
COMPILED_KEYWORD_REGEX = re.compile(pattern_str, re.IGNORECASE)


def filter_and_score_article(scraped_article: Dict[str, Any]) -> Dict[str, Any]:
    title = scraped_article.get('title', '')
    content = scraped_article.get('content', '') 
    company_name = scraped_article.get('search_keyword', '')
    
    # 1단계: 명시적 제외 필터링 (제목만 검사)
    exclusion_list = filter_rules.COMPANY_EXCLUSION_RULES.get(company_name, [])
    for exclusion_keyword in exclusion_list:
        if exclusion_keyword.lower() in title.lower():
            logging.debug(f"[Filtered-Rule] '{title}' (contains: {exclusion_keyword})")
            return {
                "passed": False, "score": 0,
                "matched_keywords": f"ExclusionRule: {exclusion_keyword}"
            }
    
    # 2단계: 관련성 스코어링 (제목 + 본문)
    content_for_scoring = f"{title} {content}" # (이제 .lower() 안 함. re.IGNORECASE가 처리)
    score = 0
    matched_keywords_list = [] # 매칭된 (원본키워드, 점수) 튜플 저장

    # 컴파일된 정규식으로 한 번에 모든 키워드 검색
    # .lower()를 content에 적용하여 정규식이 소문자 기준으로 찾도록 함
    # set()을 사용해 중복 매칭된 키워드는 1번만 카운트
    unique_found_words_lower = set(COMPILED_KEYWORD_REGEX.findall(content_for_scoring.lower()))

    # 만약 매칭된 키워드가 하나도 없다면, 즉시 탈락
    if not unique_found_words_lower:
        logging.debug(f"[Filtered-LowScore] No keywords found for '{title}'")
        return {"passed": False, "score": 0, "matched_keywords": "[]"}

    # 찾은 키워드들(소문자)을 순회하며 점수 합산
    for word_lower in unique_found_words_lower:
        # 룩업 맵에서 (원본 키워드, 점수)를 가져옴
        original_keyword, value = KEYWORD_MAP_LOWER[word_lower]
        
        score += value
        matched_keywords_list.append((original_keyword, value))
        
        # 즉시 탈락(-999) 로직은 여기서 함께 처리
        if value <= -999:
            logging.debug(f"[Filtered-Irrelevant] '{title}' (contains: {original_keyword})")
            return {
                "passed": False, "score": value,
                "matched_keywords": str(matched_keywords_list)
            } 

    # 3단계: 최종 임계값(Threshold) 검사
    if score < keywords.PASS_THRESHOLD:
        logging.debug(f"[Filtered-LowScore] Score {score} < {keywords.PASS_THRESHOLD} for '{title}'")
        return {
            "passed": False, "score": score,
            "matched_keywords": str(matched_keywords_list)
        }

    # 4단계: 최종 통과
    logging.info(f"[PASSED] Score {score} for '{title}'")
    return {
        "passed": True, "score": score,
        "matched_keywords": str(matched_keywords_list)
    }