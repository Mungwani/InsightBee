# apps/dataflow/news_pipeline/filter_rules.py
"""
[1단계] 명시적 제외 필터링 규칙
"""
COMPANY_EXCLUSION_RULES = {
    "KT": [ "KT&G", "KT알파", "KT스카이라이프", "kt wiz" ],
    "삼성전자": [ "삼성증권", "삼성생명", "삼성카드", "삼성화재", "삼성 라이온즈" ],
    "HD현대": [ "현대카드", "현대백화점" ],
    "SK": [ "SK증권" ]
}