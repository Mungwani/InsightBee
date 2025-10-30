# apps/dataflow/common/db_sa.py
import logging
from typing import Dict, Set
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession # 비동기 엔진/세션
from sqlalchemy.orm import sessionmaker # 세션 팩토리
from sqlalchemy.future import select # SQLAlchemy 2.0 스타일 select
from sqlalchemy.sql.expression import desc # 정렬(DESC)

from .. import config # [!!수정 완료!!] 상위 폴더의 config 임포트 (DB_URL_ASYNC 등)
from .models import Companies, NewsArticle # DB 테이블 스키마 (select 쿼리 시 필요)

# --- 1. 비동기 엔진 및 세션 설정 ---

# create_async_engine: 비동기 커넥션 풀 생성
async_engine = create_async_engine(
    config.DB_URL_ASYNC, # config의 비동기 DB 접속 주소
    pool_recycle=3600,   # 1시간(3600초)마다 커넥션 재활용 (Stale connection 방지)
    echo=False           # SQL 쿼리를 로그로 출력하지 않음 (True로 설정 시 디버깅 유용)
)

# AsyncSessionLocal: 세션 팩토리(공장) 생성
# 실제 DB 작업 시 이 팩토리를 호출하여 세션 인스턴스를 만듦
AsyncSessionLocal = sessionmaker(
    bind=async_engine,      # 이 팩토리는 async_engine에 바인딩됨
    class_=AsyncSession,    # 비동기 세션 클래스 사용
    expire_on_commit=False, # (중요) 커밋 후에도 객체에 접근 허용 (비동기 세션에 권장)
    autocommit=False,       # (중요) 자동 커밋 비활성화 (main.py에서 수동 관리)
    autoflush=False         # (중요) 자동 flush 비활성화 (main.py에서 수동 관리)
)

async def get_db_session() -> AsyncSession:
    """
    [비동기 제너레이터]
    main.py의 'async for session in get_db_session():' 구문에서 사용될
    DB 세션 및 트랜잭션 관리자입니다.
    
    [작동 방식]
    1. 세션을 생성 (AsyncSessionLocal())
    2. try 블록의 'yield session'에서 main.py의 로직이 실행됨
    3. main.py 로직이 성공적으로 끝나면 (에러가 없으면), 자동으로 커밋 (main.py의 session.commit())
    4. main.py 로직에서 예외(Exception)가 발생하면, 'except' 블록이 잡아서 'session.rollback()' 실행
    5. 성공/실패 여부와 관계없이 'finally' 블록에서 'session.close()'로 커넥션 반환
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session # main.py에 세션 제어권을 넘김
        except Exception:
            await session.rollback() # main.py에서 에러 발생 시 롤백
            raise # 에러를 다시 상위로 전달
        finally:
            await session.close() # 세션 닫기 (커넥션 풀에 반환)

# --- 2. 데이터 로더 함수 (main.py가 사용) ---
# 파이프라인 시작 '전'에 필요한 데이터를 DB에서 가져오는 함수들

async def load_company_map_async() -> Dict[str, int]:
    """
    [비동기] 'companies' 테이블에서 (회사명: company_id) 맵을 로드합니다.
    스크래핑 시에는 '회사명'을 사용하지만, DB 저장 시 'company_id'(FK)가 필요하기 때문입니다.
    [!!최종 수정!!] models.py 변경에 따라 Companies.id를 사용합니다.
    """
    logging.info("Loading company name-to-ID map from DB ('companies' table)...")
    # 이 함수는 파이프라인 트랜잭션과 별개로, 자체 세션을 열고 닫음
    async with AsyncSessionLocal() as session:
        try:
            # [!!핵심 수정!!] Companies.name_ko와 Companies.id를 선택
            stmt = select(Companies.name_ko, Companies.id).order_by( 
                Companies.name_ko,
                desc(Companies.id) # 혹시 모를 이름 중복 시 id가 높은(최신) 것을 사용
            )
            result = await session.execute(stmt)
            
            # (회사명, ID) 튜플 리스트를 딕셔너리로 변환
            company_map = {name: company_id for name, company_id in result.all()}
            
            logging.info(f"Loaded {len(company_map)} unique company mappings.")
            if not company_map:
                logging.warning("Company map is empty. 'companies' table may be empty.")
            return company_map
            
        except Exception as e:
            logging.error(f"Failed to load company map: {e}")
            return {}

async def get_existing_url_hashes_async() -> Set[str]:
    """
    [비동기] 'news_articles' 테이블에서 이미 수집된 모든 url_hash를 Set으로 로드합니다.
    Naver API 수집 단계에서 중복 수집을 방지하기 위해 사용됩니다. (메모리 효율적)
    """
    logging.info("Loading existing URL hashes from 'news_articles' table...")
    async with AsyncSessionLocal() as session:
        try:
            # NewsArticle 테이블에서 url_hash 컬럼만 선택
            stmt = select(NewsArticle.url_hash)
            result = await session.execute(stmt)
            
            # .scalars()로 (hash,) 튜플이 아닌 hash 값(스칼라) 리스트를 가져옴
            # set()으로 변환하여 scraper.py에서 O(1) 시간 복잡도로 조회(in) 가능하게 함
            hashes = set(result.scalars().all())
            logging.info(f"Loaded {len(hashes)} existing URL hashes.")
            return hashes
            
        except Exception as e:
            # (중요) DB가 비어있거나 테이블이 없는 첫 실행 시, 에러 대신 경고
            logging.warning(f"Failed to load existing hashes (Table may not exist yet): {e}")
            return set() # 빈 Set을 반환하여 파이프라인이 정상 진행되도록 함