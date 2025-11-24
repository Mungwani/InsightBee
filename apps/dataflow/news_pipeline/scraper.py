# apps/dataflow/news_pipeline/scraper.py
import asyncio
import aiohttp
import logging
import hashlib
from typing import List, Dict, Set, Optional, Any, Callable
from urllib.parse import urlparse
from tqdm.asyncio import tqdm
from datetime import datetime

# 스크래핑 라이브러리
import trafilatura # HTML에서 본문을 추출
from newspaper import Article # HTML에서 제목, 날짜 등을 추출
from bs4 import BeautifulSoup # 특정 규칙(SPIDER_RULES)을 적용하기 위한 HTML 파서
from selenium import webdriver # Javascript 렌더링이 필요한 사이트용
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager # ChromeDriver 자동 설치/관리

# 비동기 DB 세션 및 모델 임포트
from sqlalchemy.ext.asyncio import AsyncSession
from ..common.models import NewsArticle # DB에 저장될 Article 객체 모델

from .. import config # 설정 임포트

# 날짜 파싱 코드
def parse_date(date_obj: Any) -> Optional[datetime]:
    """scraper가 반환한 datetime 객체 또는 None을 처리"""
    if isinstance(date_obj, datetime):
        if date_obj.tzinfo: return date_obj.replace(tzinfo=None)
        return date_obj
    return None

def create_db_object(
    scraped_data: Dict[str, Any], 
    filter_result: Dict[str, Any], 
    company_map: Dict[str, int]
) -> Optional[NewsArticle]:
    """
    스크래핑된 데이터와 필터링 결과를 바탕으로 NewsArticle DB 객체를 생성합니다.
    """
    company_name = scraped_data['search_keyword']
    company_id = company_map.get(company_name) # 회사명(str)을 company_id(int)로 변환
    
    if not company_id:
        # company_map에 회사가 없는 경우 
        logging.warning(f"Skipping article (company_id not found for '{company_name}'): {scraped_data['url']}")
        return None

    # NewsArticle 모델 인스턴스 생성
    return NewsArticle(
        company_id=company_id,
        title=scraped_data.get('title', scraped_data.get('api_title', '제목 없음')), # 파싱 실패 시 API 제목 사용
        url=scraped_data['url'],
        url_hash=scraped_data['url_hash'],
        content=scraped_data.get('content'),
        published_at=parse_date(scraped_data.get('published_at')),
        
        search_keyword=company_name,
        score=filter_result['score'],
        matched_keywords=filter_result['matched_keywords'],
        
        is_passed_rule=filter_result['passed']          
    )

# --- 1. Naver API 링크 수집 ---
async def fetch_naver_links_for_company(session: aiohttp.ClientSession, company: str, semaphore: asyncio.Semaphore) -> List[Dict[str, str]]:
    headers = {"X-Naver-Client-Id": config.NAVER_CLIENT_ID, "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET}
    all_valid_links = [] # 수집된 링크(dict)를 저장 리스트
    
    # start_index 1부터 (최대 1000까지) 100개(ARTICLES_PER_PAGE)씩 증가하며 API 호출
    for start_index in range(1, config.TARGET_ARTICLES_PER_COMPANY + 1, config.ARTICLES_PER_PAGE):
        if start_index > 1000: break # Naver API는 1000 이상 조회를 막음
        await asyncio.sleep(0.5) # Naver API 속도 제한 (0.1 -> 0.2)(초당 10회)

        api_url = f"https://openapi.naver.com/v1/search/news.json?query={company}&display={config.ARTICLES_PER_PAGE}&start={start_index}&sort=date"
        
        async with semaphore: # 동시 요청 수 제어
            try:
                async with session.get(api_url, headers=headers, timeout=config.REQUEST_TIMEOUT) as response:
                    if response.status == 429: # 429: Rate Limit (요청 한도 초과)
                        logging.warning(f"Rate limit hit for '{company}'. Retrying...")
                        await asyncio.sleep(1) # 1초 대기 후 재시도
                        response = await session.get(api_url, headers=headers, timeout=config.REQUEST_TIMEOUT)

                    response.raise_for_status() # 4xx, 5xx 에러 시 예외 발생
                    data = await response.json()
                    items = data.get('items', [])
                    if not items: break
                    for item in items:
                        link = item.get('originallink') or item.get('link', '')
                        if link.startswith('http'):
                            try:
                                # 'naver.com' 같은 링크는 제외하고, 'chosun.com' 등 언론사 도메인만 추출
                                host = '.'.join(urlparse(link).hostname.split('.')[-2:])
                                if host in config.ALLOWED_PRESS_HOSTS:
                                    all_valid_links.append({
                                        'url': link, 
                                        'press': host, 
                                        'search_keyword': company,
                                        'api_title': item.get('title', '').replace('<b>', '').replace('</b>', ''), # HTML 태그 제거
                                        'api_pubDate': item.get('pubDate', '')
                                    })
                            except (AttributeError, IndexError): continue # 유효하지 않은 URL 파싱 스킵
            except Exception as e: # 에러 발생 시 해당 회사 수집 중단
                logging.error(f"Failed to fetch links for '{company}' (start: {start_index}): {e}")
                break
    return all_valid_links

async def collect_all_links(companies: List[str], existing_url_hashes: Set[str]) -> List[Dict[str, str]]:
    """
    [비동기] 모든 대상 회사(companies)에 대해 링크 수집을 병렬로 실행합니다.
    DB에 이미 수집된 링크(existing_url_hashes)는 제외하고 신규 링크만 반환합니다.
    """
    logging.info(f"Starting link collection for {len(companies)} companies...")
    semaphore = asyncio.Semaphore(config.CONCURRENT_REQUESTS_LINKS) # API 동시 요청 수 제어
    async with aiohttp.ClientSession() as session:
        # 모든 회사에 대해 fetch_naver_links_for_company 태스크 생성
        tasks = [fetch_naver_links_for_company(session, company, semaphore) for company in companies]
        # tqdm으로 진행률을 표시하며 모든 태스크를 병렬 실행
        results = await tqdm.gather(*tasks, desc="1. Fetching Links (API)")

        # -- 중복 제거 --
        unique_new_links = []
        seen_hashes = set(existing_url_hashes)

        # 2차원 리스트(results)를 1차원으로 풀면서 순회
        for link_info in (link for sublist in results for link in sublist):
            url_hash = hashlib.md5(link_info['url'].encode()).hexdigest() # URL 해시 생성
            if url_hash not in seen_hashes: # 이번에 새로 수집된 링크인지 확인
                link_info['url_hash'] = url_hash
                unique_new_links.append(link_info)
                seen_hashes.add(url_hash)# 방금 추가한 해시도 seen에 추가 (API 결과 내 중복 방지)

        logging.info(f"Collected {len(unique_new_links)} new unique links to scrape.")
        return unique_new_links

# --- 2. 기사 본문 스크래핑 (핵심 로직) ---
def _parse_content_common(url: str, html: str, press: str) -> Dict[str, Any]:
    """
    [동기] HTML 문자열을 받아 본문, 제목, 날짜를 파싱하는 공통 로직
    (aiohttp, Selenium 스크래퍼가 모두 이 함수를 사용)
    """
    text = ""; soup = BeautifulSoup(html, 'html.parser')

    # 1. 특정 언론사 규칙(SPIDER_RULES)이 있으면 우선 적용
    if press in config.SPIDER_RULES:
        text_area = soup.select_one(config.SPIDER_RULES[press])
        if text_area: text = text_area.get_text(strip=True)
    # 2. 규칙이 없거나 실패 -> trafilatura 로 본문 자동 추출
    if not text: text = trafilatura.extract(html)

    # 3. 본문 추출 실패 시 (너무 짧아서) 에러 발생
    if not text or len(text) < 100: raise ValueError("Extracted text is too short.")

    # 4. newspaper 라이브러리로 제목(title)과 발행일(publish_date) 추출
    article = Article(url, language='ko'); article.set_html(html); article.parse()
    if not article.title: raise ValueError("Failed to parse article title.")
    return {"title": article.title, "content": text, "published_at": article.publish_date}

def _create_selenium_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox"); options.add_argument("--disable-dev-shm-usage"); options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    try:
        logging.info("Attempting to initialize ChromeDriver via Selenium Manager...")
        driver = webdriver.Chrome(options=options)
        logging.info("ChromeDriver initialized successfully.")
        return driver
    except Exception as e:
        logging.critical(f"Failed to initialize Selenium Driver: {e}")
        raise

def scrape_article_robust_sync(link_info: Dict) -> Optional[Dict]:
    """
    [동기] Selenium을 사용하여 기사 1개를 스크래핑합니다.
    (이 함수는 동기 함수이므로, 비동기 loop.run_in_executor를 통해 별도 스레드에서 실행되어야 함)
    """
    url = link_info['url']; driver = None
    try:
        # 드라이버 생성 및 페이지 접속
        driver = _create_selenium_driver(); driver.get(url)
        # config의 TIMEOUT 시간 동안 <body> 태그가 로드될 때 까지 대기
        WebDriverWait(driver, config.REQUEST_TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # 렌더링이 완료된 HTML 소스 가져오기
        html_content = driver.page_source

        # 공통 파싱 함수 호출
        parsed_data = _parse_content_common(url, html_content, link_info['press'])
        # 기존 link_info 딕셔너리에 파싱된 데이터(title, content 등)를 합쳐서 반환
        return {**link_info, **parsed_data}
    except Exception as e:
        logging.error(f"Selenium scraping FAILED for {url} - {e}")
        # 실패 시, 본문/제목이 없더라도 API 제목 등 기본 정보만 반환
        return link_info 
    finally:
        if driver: driver.quit()

# --- 3."스트림" 방식의 파이프라인 ---
# main.py가 이 함수들을 호출.

async def scrape_and_process_fast(
    session: aiohttp.ClientSession, # main.py의 aiohttp 세션
    link_info: Dict,                # 수집된 링크 정보
    semaphore: asyncio.Semaphore,   # 동시 실행 제어용 세마포
    db_session: AsyncSession,       # main.py의 DB 세션
    company_map: Dict[str, int],    # 회사-ID 맵
    filter_func: Callable           # filter.py의 필터링 함수
) -> Optional[Dict]:
    """
    [고속 스트림] aiohttp 스크래핑 -> 필터링 -> DB 세션에 추가
    - 성공 시: None 반환
    - 실패/JS 필요 시: Selenium 재시도를 위해 link_info 딕셔너리 반환
    """
    url = link_info['url']
    async with semaphore: # 동시 실행 제어
        scraped_data = None
        try:
            # 1. config에 지정된 'JS 필요 사이트'인지 확인
            if link_info['press'] in config.JAVASCRIPT_REQUIRED_SITES:
                return link_info # Selenium 재시도 (즉시 반환)
            
            # 2. [aiohttp] 비동기로 HTML 다운로드
            async with session.get(url, timeout=config.REQUEST_TIMEOUT) as response:
                html_content = await response.text()
            
            # 3. [파싱] 공통 파싱 함수 호출
            parsed_data = _parse_content_common(url, html_content, link_info['press'])
            scraped_data = {**link_info, **parsed_data}# 원본 link_info와 파싱 결과 결합
            
        except Exception as e:
            # aiohttp 실패 (타임아웃, 본문/제목 파싱 실패 등)
            logging.error(f"Fast Scrape FAILED for {url} (Reason: {e}). Retrying with Selenium.")
            return link_info # Selenium 재시도

        # [스크래핑 성공 시]
        try:
            # 4. [필터링] main.py로부터 전달받은 filter_func 즉시 호출
            filter_result = filter_func(scraped_data)

            # 5. [DB 객체 생성]
            db_article = create_db_object(scraped_data, filter_result, company_map)
            if db_article:
                # 6. [DB 세션에 추가] main.py의 세션에 객체를 추가 (커밋X, 추가만)
                db_session.add(db_article)
            return None # 성공
        # 필터링 또는 DB 객체 생성/추가 실패 시
        except Exception as e:
            logging.error(f"Fast Scrape Filtering/DB-Add FAILED for {url}: {e}")
            return None # DB 저장 실패 시 재시도 안 함

async def scrape_and_process_robust(
    link_info: Dict,                # 재시도 대상 링크 정보
    semaphore: asyncio.Semaphore,   # Selenium용 세마포 (동시 실행 수 적음)
    db_session: AsyncSession,       # main.py의 DB 세션
    company_map: Dict[str, int],    # 회사-ID 맵
    filter_func: Callable,          # filter.py의 필터링 함수
    loop: asyncio.AbstractEventLoop # run_in_executor용 이벤트 루프
):
    """
    [안정 스트림] Selenium 스크래핑 -> 필터링 -> DB 세션에 추가
    (이 함수는 반환값이 없음. 성공/실패 모두 여기서 처리)
    """
    url = link_info['url']
    async with semaphore: # 동시 실행 제어
        scraped_data = None
        try:
            # 1. [Selenium] 동기 함수인 scrape_article_robust_sync를
            #    별도 스레드에서 실행 (비동기 루프를 막지 않기 위함)
            scraped_data = await loop.run_in_executor(None, scrape_article_robust_sync, link_info)

            if not scraped_data:
                # scrape_article_robust_sync가 치명적 오류로 None을 반환한 경우)
                return 
            
        except Exception as e:
            logging.error(f"Robust Scrape Executor FAILED for {url}: {e}")
            return # 스레드 실행 자체 실패 시 중단

        # [스크래핑 성공 (또는 부분 성공) 시]
        try:
            # 2. [필터링] main.py로부터 전달받은 filter_func 즉시 호출
            # (Selenium이 본문 파싱에 실패했더라도, API 제목이라도 있으면 필터링 시도)
            filter_result = filter_func(scraped_data)
            # 3. 즉시 DB 객체 생성
            db_article = create_db_object(scraped_data, filter_result, company_map)
            if db_article:
                # 4. 즉시 DB 세션에 추가 (커밋은 main에서 한 번에)
                db_session.add(db_article)

        except Exception as e:
            # 필터링 또는 DB 객체 생성/추가 실패 시
            logging.error(f"Robust Scrape Filtering/DB-Add FAILED for {url}: {e}")