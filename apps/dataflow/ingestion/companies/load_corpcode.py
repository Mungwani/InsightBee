from apps.dataflow.common.dart import fetch_corpcode_zip, parse_corpcode_xml
from apps.dataflow.common.db_sa import SessionLocal
from apps.dataflow.common.models import Company
from sqlalchemy.dialects.postgresql import insert

WHITELIST: set[str] = {
    "삼성전자",
    "SK하이닉스",
    "LG에너지솔루션",
    "삼성바이오로직스",
    "두산에너빌리티",
    "현대자동차",
    "한화에어로스페이스",
    "HD현대중공업",
    "기아",
    "KB금융",
    "셀트리온",
    "NAVER",
    "삼성물산",
    "신한지주",
    "SK스퀘어",
    "한화오션",
    "삼성생명",
    "HD한국조선해양",
    "현대모비스",
    "한국전력공사",
    "카카오",
    "HD현대일렉트릭",
    "하나금융지주",
    "LG화학",
    "POSCO홀딩스",
    "고려아연",
    "알테오젠",
    "현대로템",
    "HMM",
    "삼성SDI",
    "삼성화재해상보험",
    "삼성중공업",
    "SK이노베이션",
    "메리츠금융지주",
    "우리금융지주",
    "포스코퓨처엠",
    "케이티앤지",
    "SK",
    "에코프로비엠",
    "삼성전기",
    "기업은행",
    "효성중공업",
    "LG전자",
    "한미반도체",
    "크래프톤",
    "HD현대",
    "삼성에스디에스",
    "케이티",
    "현대글로비스",
}


def _norm_name(s: str | None) -> str | None:
    if s is None:
        return None
    collapsed = " ".join(s.split())
    return collapsed


def _is_whitelisted(name_ko: str | None) -> bool:
    if not name_ko:
        return False
    return _norm_name(name_ko) in {_norm_name(n) for n in WHITELIST}

def upsert_rows(session, rows: list[dict]) -> None:
    ins = insert(Company).values(rows)
    stmt = ins.on_conflict_do_update(
        index_elements=[Company.corp_code], 
        set_={
            "name_ko":     ins.excluded.name_ko,
            "name_en":     ins.excluded.name_en,
            "stock_code":  ins.excluded.stock_code,
        },
    )
    session.execute(stmt)

def main():
    zip_bytes = fetch_corpcode_zip()
    all_rows = parse_corpcode_xml(zip_bytes)
    rows = [r for r in all_rows if _is_whitelisted(r.get("name_ko"))]

    print(f"[corpcode] filtered rows for whitelist: {len(rows)}")
    if not rows:
        print("[corpcode] WARNING: no rows matched whitelist. Check names/spaces.")
        return

    with SessionLocal() as s:
        upsert_rows(s, rows)
        s.commit()

    missing = [n for n in WHITELIST if _norm_name(n) not in {r['name_ko'] for r in rows}]
    if missing:
        print("[corpcode] NOTE: some whitelist names not found in DART corpCode:", missing)

    print("[corpcode] upsert done for whitelist.")

if __name__ == "__main__":
    main()
