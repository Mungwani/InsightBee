# apps/dataflow/news_pipeline/main.py
import asyncio
import logging
import time
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional
from tqdm.asyncio import tqdm

from dotenv import load_dotenv
load_dotenv()

# DB 및 모델
from ..common.db_sa import (
    get_db_session, 
    load_company_map_async, 
    get_existing_url_hashes_async,
    async_engine 
)
from ..common.models import NewsArticle, Base 

# 파이프라인 모듈
from . import scraper # 1. 링크 수집 2. 본문 스크래핑
from . import filter  # 3. 기사 필터링
from . import clustering # [NEW] 4. AI 중복 제거 모듈 추가
from .. import config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def setup_database_tables():
    """
    Base에 등록된 모든 테이블 중 존재하지 않는 테이블만 생성합니다.
    """
    logging.info("Attempting to create tables (will skip existing ones)...")
    async with async_engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all) 
            logging.info("All necessary tables created/checked successfully.")
        except Exception as e:
            logging.critical(f"FATAL DB SETUP ERROR: {e}")
            raise 


async def main_pipeline():
    start_time = time.time() # 전체 실행 시간 측정 시작
    
    # --- 0. DB 준비 (초기 데이터 로드) ---
    try:
        company_map = await load_company_map_async()
        if not company_map:
            logging.error("Company map is empty. Cannot proceed."); return
        
        existing_url_hashes = await get_existing_url_hashes_async()
        
    except Exception as e:
        logging.critical(f"Failed to connect or load initial data: {e}"); return 

    # --- 1. 수집 대상 기업 선정 ---
    target_companies = list(company_map.keys()) 
    if not target_companies:
        logging.info("No target companies found. Exiting."); return
        
    logging.info(f"Starting pipeline for {len(target_companies)} companies.")

    # --- 2. 링크 수집 (Naver API) ---
    links_to_scrape = await scraper.collect_all_links(target_companies, existing_url_hashes)
    
    # 신규 링크가 없더라도 클러스터링(중복제거) 로직은 돌려야 할 수 있으므로 바로 리턴하지 않고 체크
    if links_to_scrape:
        
        # --- 단일 DB 트랜잭션 시작 (스크래핑용) ---
        async for session in get_db_session():
            async with aiohttp.ClientSession() as aio_session: 
                try:
                    # --- 3. 고속 스크래핑 (aiohttp) ---
                    logging.info(f"Starting Phase 1: Fast Scrape (aiohttp) for {len(links_to_scrape)} links...")
                    semaphore_fast = asyncio.Semaphore(config.CONCURRENT_REQUESTS_SCRAPE_FAST)
                    
                    fast_tasks = []
                    for link in links_to_scrape:
                        task = scraper.scrape_and_process_fast(
                            aio_session, 
                            link, 
                            semaphore_fast, 
                            session, 
                            company_map, 
                            filter.filter_and_score_article
                        )
                        fast_tasks.append(task)
                    
                    results = await tqdm.gather(*fast_tasks, desc="2. Fast Scrape (aiohttp)")
                    failed_links_for_selenium = [res for res in results if res is not None]
                    
                    logging.info(f"Phase 1 Complete. {len(links_to_scrape) - len(failed_links_for_selenium)} success, {len(failed_links_for_selenium)} retries.")

                    # --- 4. 안정 스크래핑 (Selenium) ---
                    if failed_links_for_selenium: 
                        logging.info(f"Starting Phase 2: Robust Scrape (Selenium) for {len(failed_links_for_selenium)} links...")
                        semaphore_robust = asyncio.Semaphore(config.CONCURRENT_SELENIUM_TASKS)
                        loop = asyncio.get_running_loop()
                        robust_tasks = []

                        for link in failed_links_for_selenium:
                            task = scraper.scrape_and_process_robust(
                                link, semaphore_robust, session, company_map, 
                                filter.filter_and_score_article, loop
                            )
                            robust_tasks.append(task)
                        
                        await tqdm.gather(*robust_tasks, desc="3. Robust Scrape (Selenium)")
                    
                    # --- 5. 스크래핑 결과 커밋 ---
                    logging.info("All scraping finished. Committing changes to DB...")
                    await session.commit()
                    logging.info("Successfully committed all articles to DB.")

                except Exception as e:
                    logging.error(f"An error occurred during the pipeline: {e}")
                    await session.rollback()
                    logging.warning("Session rolled back due to error.")
    else:
        logging.info("No new links to scrape. Skipping scraping phase.")

    # --- 6. [NEW] 후처리: AI 중복 제거 (클러스터링) ---
    # 스크래핑 트랜잭션과 별도로 실행하여, 스크래핑이 성공했다면 클러스터링도 시도
    try:
        logging.info("--- Starting Post-Processing Phase ---")
        await clustering.run_clustering_process()
    except Exception as e:
        # 클러스터링 실패가 전체 파이프라인의 실패로 간주되진 않도록 로그만 남김
        logging.error(f"Clustering process failed: {e}")

    end_time = time.time()
    logging.info(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    # 1. (최초 1회) 테이블 생성
    # asyncio.run(setup_database_tables()) 
    
    # 2. 메인 파이프라인 실행
    asyncio.run(main_pipeline())