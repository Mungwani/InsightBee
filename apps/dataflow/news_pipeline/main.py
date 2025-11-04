# apps/dataflow/news_pipeline/main.py
import asyncio
import logging
import time
import aiohttp  # [!! 수정 1 !!] aiohttp 임포트 확인 (이미 되어있네요)
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
from .. import config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)


# 테이블 체크 함수
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
        # companies 테이블에서 회사명(company_id) 로드
        company_map = await load_company_map_async()
        if not company_map:
            logging.error("Company map is empty. Cannot proceed."); return
        
        # news_articles'테이블에서 기존 URL 해시 Set 로드(중복 방지)
        existing_url_hashes = await get_existing_url_hashes_async()
        
    except Exception as e:
        logging.critical(f"Failed to connect or load initial data: {e}"); return 

    # --- 1. 수집 대상 기업 선정 ---
    # company_map의 key[회사명] 목록을 수집 대상으로 지정
    target_companies = list(company_map.keys()) 
    if not target_companies:
        logging.info("No target companies found. Exiting."); return
        
    logging.info(f"Starting pipeline for {len(target_companies)} companies.")

    # --- 2. 링크 수집 (Naver API) ---
    # scraper가 Naver API를 호출하여 새롭고 유효한 링크만 수집
    links_to_scrape = await scraper.collect_all_links(target_companies, existing_url_hashes)
    if not links_to_scrape:
        logging.info("No new articles to scrape. Job finished."); return

    # --- 단일 DB 트랜잭션 시작 ---
    # 'session'은 DB 세션입니다.
    async for session in get_db_session():
        
        # [!! 수정 2 !!] aiohttp 세션을 'aio_session'이라는 *다른* 이름으로 생성
        # 이 세션(aio_session)이 웹 요청(aiohttp.get)을 담당합니다.
        async with aiohttp.ClientSession() as aio_session: 
            try:
                # --- 3. 고속 스크래핑 (aiohttp) ---
                logging.info(f"Starting Phase 1: Fast Scrape (aiohttp) for {len(links_to_scrape)} links...")
                # config 파일의 설정값으로 동시 요청 수 제한
                semaphore_fast = asyncio.Semaphore(config.CONCURRENT_REQUESTS_SCRAPE_FAST)
                
                fast_tasks = []
                for link in links_to_scrape:
                    task = scraper.scrape_and_process_fast(
                        aio_session, # [!! 수정 3 !!] 첫 번째 인자를 'session'이 아닌 'aio_session'(웹 세션)으로 변경
                        link, 
                        semaphore_fast, 
                        session, # [!!] 네 번째 인자는 'session'(DB 세션)이 맞습니다.
                        company_map, 
                        filter.filter_and_score_article # 필터 함수 전달
                    )
                    fast_tasks.append(task)
                
                # 생성된 모든 테스크를 asyncio.gather로 병렬 실행(tqdm으로 진행률 표시)
                results = await tqdm.gather(*fast_tasks, desc="2. Fast Scrape (aiohttp)")

                # 테스트 결과가 None이 아닌 것(실패한 링크)들을 리스트로 수집
                failed_links_for_selenium = [res for res in results if res is not None]
                
                logging.info(f"Phase 1 Complete. {len(links_to_scrape) - len(failed_links_for_selenium)} success, {len(failed_links_for_selenium)} retries.")

                # --- 4. 안정 스크래핑 (Selenium) ---
                if failed_links_for_selenium: #1단계 실패 링크 있을 경우에만 실행
                    logging.info(f"Starting Phase 2: Robust Scrape (Selenium) for {len(failed_links_for_selenium)} links...")
                    
                    # Selenium은 리소스를 많이 사용하므로 동시 실행 수를 낮게 설정
                    semaphore_robust = asyncio.Semaphore(config.CONCURRENT_SELENIUM_TASKS)
                    loop = asyncio.get_running_loop()
                    robust_tasks = []

                    for link in failed_links_for_selenium:
                        # selenium 테스트 생성( 스크래핑 -> 필터링 -> session.add)작업
                        task = scraper.scrape_and_process_robust(
                            link, semaphore_robust, session, company_map, 
                            filter.filter_and_score_article, loop
                        )
                        robust_tasks.append(task)
                    
                    # Selenium 태스크 실행
                    await tqdm.gather(*robust_tasks, desc="3. Robust Scrape (Selenium)")
                
                # --- 5. 최종 커밋 ---
                # 3, 4단계에서 session.add()로 메모리에 추가된 모든 변경사항을 DB에 커밋한번으로 올림.
                logging.info("All scraping finished. Committing changes to DB...")
                await session.commit()
                logging.info("Successfully committed all articles to DB.")

            except Exception as e:
                # 3,4,5단계 중 에러 발생
                logging.error(f"An error occurred during the pipeline: {e}")
                # 롤백
                await session.rollback()
                logging.warning("Session rolled back due to error.")

    end_time = time.time()
    logging.info(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    
    # [!!] 버그 2 ('is_relevant_human') 해결을 위해 캐시를 삭제하세요! [!!]
    # 터미널에서 `find . -type d -name "__pycache__" -exec rm -rf {} +` 실행
    
    # 1. (최초 1회) 테이블 생성
    # asyncio.run(setup_database_tables()) 
    
    # 2. (1번 완료 후) 메인 파이프라인 실행
    asyncio.run(main_pipeline())