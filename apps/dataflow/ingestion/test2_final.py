import asyncio
import aiohttp
import time
import csv
import os
import logging
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse

from newspaper import Article
import trafilatura
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 로깅 설정 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- API 키 및 크롤링 설정 ---
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "klkCe1zaN1YXD44JqezW")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "2E8To4pAYj")
ARTICLES_PER_COMPANY = 100
CSV_FILENAME = "news_scraping_results_final2.csv"
CONCURRENT_REQUESTS_LINKS = 5
CONCURRENT_REQUESTS_SCRAPE = 50
REQUEST_TIMEOUT = 15

# --- 언론사 및 사이트 분류 ---
ALLOWED_PRESS_HOSTS = {
    'chosun.com', 'joongang.co.kr', 'donga.com', 'hani.co.kr', 'khan.co.kr', 'seoul.co.kr',
    'kmib.co.kr', 'munhwa.com', 'segye.com', 'hankookilbo.com', 'news.kbs.co.kr',
    'imnews.imbc.com', 'news.sbs.co.kr', 'ytn.co.kr', 'yonhapnewstv.co.kr', 'jtbc.co.kr',
    'ichannela.com', 'mbn.co.kr', 'tvchosun.com', 'yna.co.kr', 'newsis.com', 'news1.kr',
    'hankyung.com', 'mk.co.kr', 'edaily.co.kr', 'asiae.co.kr', 'wowtv.co.kr', 'fnnews.com',
    'sedaily.com', 'heraldcorp.com', 'moneys.co.kr', 'sentv.co.kr', 'etoday.co.kr',
}
JAVASCRIPT_REQUIRED_SITES = {'imnews.imbc.com', 'news.sbs.co.kr', 'jtbc.co.kr'}

# 1. 뉴스 링크 수집 (Naver Search API)
async def fetch_news_links_for_company(
    session: aiohttp.ClientSession, company: str, semaphore: asyncio.Semaphore
) -> List[Dict[str, str]]:
    """특정 기업의 네이버 뉴스 링크를 수집하며, 429 에러 시 재시도합니다."""
    api_url = f"https://openapi.naver.com/v1/search/news.json?query={company}&display={ARTICLES_PER_COMPANY}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    
    async with semaphore:
        for attempt in range(3): # 최대 3번 시도
            try:
                # 요청 간의 기본 간격을 둠
                await asyncio.sleep(0.2)
                
                async with session.get(api_url, headers=headers, timeout=REQUEST_TIMEOUT) as response:
                    if response.status == 429:
                        logging.warning(f"Rate limit for '{company}'. Retrying after {2 * (attempt + 1)}s...")
                        await asyncio.sleep(2 * (attempt + 1)) # 재시도 간격을 점차 늘림
                        continue
                    
                    response.raise_for_status()
                    data = await response.json()
                    items = data.get('items', [])
                    
                    valid_links = []
                    for item in items:
                        link = item.get('originallink') or item.get('link', '')
                        if not link.startswith('http'): continue
                        try:
                            host = '.'.join(urlparse(link).hostname.split('.')[-2:])
                            if host in ALLOWED_PRESS_HOSTS:
                                valid_links.append({'url': link, 'press': host, 'search_keyword': company})
                        except (AttributeError, IndexError): continue
                    return valid_links # 성공 시 즉시 반환
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.error(f"Failed to fetch links for '{company}' on attempt {attempt+1}: {e}")
                await asyncio.sleep(1)
                
    logging.error(f"All retries failed for '{company}'. Skipping.")
    return [] # 모든 재시도 실패 시

async def collect_all_news_links(companies: List[str]) -> List[Dict[str, str]]:
    """모든 기업의 뉴스 링크를 비동기적으로 수집합니다."""
    logging.info("Starting to collect news links for all companies asynchronously.")
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS_LINKS)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_news_links_for_company(session, company, semaphore) for company in companies]
        results = await asyncio.gather(*tasks)
        return [link for sublist in results for link in sublist]

# 2. 기사 본문 스크래핑
def create_selenium_driver() -> webdriver.Chrome:
    """헤드리스 모드의 안정적인 Selenium Chrome 드라이버를 생성합니다."""
    options = Options()
    options.add_argument("--headless"); options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage"); options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/5.37.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/5.36")
    service = Service()
    return webdriver.Chrome(service=service, options=options)

async def scrape_article_fast(session: aiohttp.ClientSession, link_info: Dict, semaphore: asyncio.Semaphore) -> Tuple[Optional[Dict], Optional[Dict]]:
    """(1차) aiohttp와 trafilatura를 사용해 빠르게 본문을 수집합니다."""
    url = link_info['url']
    async with semaphore:
        try:
            if link_info['press'] in JAVASCRIPT_REQUIRED_SITES: return None, link_info
            async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
                html_content = await response.text()
            text = trafilatura.extract(html_content)
            if not text or len(text) < 100: raise ValueError("Extracted text is too short.")
            article = Article(url, language='ko'); article.set_html(html_content); article.parse()
            if not article.title: raise ValueError("Failed to parse article title.")
            return {"기업명": link_info['search_keyword'], "제목": article.title, "작성일": article.publish_date,
                    "본문": text, "신문사": link_info['press'], "링크": url, "비고": "정상 (1차)"}, None
        except Exception:
            return None, link_info

def scrape_article_robust(link_info: Dict) -> Optional[Dict]:
    """(2차) Selenium을 사용해 JS 렌더링이 필요한 페이지나 1차 실패 건을 안정적으로 수집합니다."""
    url = link_info['url']
    logging.info(f"Processing with Selenium: {url}")
    driver = None
    try:
        driver = create_selenium_driver()
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        html_content = driver.page_source
        text = trafilatura.extract(html_content)
        article = Article(url, language='ko'); article.set_html(html_content); article.parse()
        if not article.title or not text or len(text) < 50: raise ValueError("Failed to parse content with Selenium.")
        return {"기업명": link_info['search_keyword'], "제목": article.title, "작성일": article.publish_date,
                "본문": text, "신문사": link_info['press'], "링크": url, "비고": "정상 (2차)"}
    except Exception as e:
        logging.error(f"Selenium scraping ultimately failed for {url} - {e}")
        return None
    finally:
        if driver: driver.quit()

# 3. 데이터 저장
def save_articles_to_csv(articles: List[Dict], filename: str) -> None:
    """CSV 파일로 저장합니다."""
    if not articles: logging.warning("No articles to save."); return
    processed_articles = []
    for article in articles:
        new_article = article.copy()
        if '본문' in new_article and new_article['본문']:
            new_article['본문'] = new_article['본문'].replace('\n', ' ').replace('\r', ' ')
        processed_articles.append(new_article)
    fieldnames = ['기업명', '제목', '작성일', '본문', '신문사', '링크', '비고']
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader(); writer.writerows(processed_articles)
        logging.info(f"Successfully saved {len(processed_articles)} articles to '{filename}'.")
    except IOError as e:
        logging.error(f"Failed to write to CSV file {filename}: {e}")

# 4. Main Execution
async def main():
    start_time = time.time()
    target_companies = [
        "삼성전자", "SK하이닉스", "LG에너지솔루션", "삼성바이오로직스", "삼성전자우", "한화에어로스페이스", "HD현대중공업", 
        "현대차", "KB금융", "두산에너빌리티", "기아", "셀트리온", "NAVER", "신한지주", "한화오션", "삼성물산", 
        "삼성생명", "SK스퀘어", "HD한국조선해양", "현대모비스", "카카오", "알테오젠", "현대로템", "하나금융지주", 
        "한국전력", "HD현대일렉트릭", "POSCO홀딩스", "HMM", "삼성화재", "메리츠금융지주", "LG화학", "우리금융지주", 
        "삼성중공업", "고려아연", "SK이노베이션", "삼성SDI", "SK", "KT&G", "기업은행", "삼성전기", "크래프톤", 
        "효성중공업", "포스코퓨처엠", "HD현대", "KT", "삼성에스디에스", "LG전자", "미래에셋증권", "현대글로비스", "SK텔레콤"
    ]
    logging.info(f"Starting scraping for {len(target_companies)} companies: {target_companies}")
    news_links = await collect_all_news_links(target_companies)
    logging.info(f"Collected a total of {len(news_links)} valid news links.")
    if not news_links: return

    logging.info("Starting Phase 1: High-speed scraping...")
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS_SCRAPE)
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_article_fast(session, link, semaphore) for link in news_links]
        results = await asyncio.gather(*tasks)
    scraped_articles = [res[0] for res in results if res[0] is not None]
    failed_links_for_selenium = [res[1] for res in results if res[1] is not None]
    logging.info(f"Phase 1 Complete: {len(scraped_articles)} successful, {len(failed_links_for_selenium)} require retry.")

    if failed_links_for_selenium:
        logging.info("Starting Phase 2: Robust scraping for failed links (sequentially)...")
        for link_info in failed_links_for_selenium:
            selenium_result = scrape_article_robust(link_info)
            if selenium_result: scraped_articles.append(selenium_result)
            await asyncio.sleep(1)

    save_articles_to_csv(scraped_articles, CSV_FILENAME)
    end_time = time.time()
    logging.info(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    if NAVER_CLIENT_ID == "YOUR_ID" or NAVER_CLIENT_SECRET == "YOUR_SECRET":
        logging.warning("Please set your Naver API credentials.")
    else:
        asyncio.run(main())