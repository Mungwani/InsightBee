import requests  # 웹 페이지에 HTTP 요청을 보내기 위한 라이브러리
from bs4 import BeautifulSoup  # HTML 코드를 분석하고 원하는 정보를 쉽게 추출하기 위한 라이브러리
from newspaper import Article  # 뉴스 기사 본문, 제목, 작성일 등을 자동으로 추출해주는 라이브러리
import os  # 운영체제와 상호작용하기 위한 라이브러리 (파일/폴더 관리 등)
import csv  # CSV형식의 파일을 읽고 쓰기 위한 라이브러리
from datetime import datetime  # 날짜와 시간 관련 처리를 위한 라이브러리
import time  # 프로그램 실행 중 지연 시간 등을 주기 위한 라이브러리
from multiprocessing import Pool, cpu_count  # 여러 작업을 동시에 병렬로 처리하여 속도를 높이기 위한 라이브러리

# --- Selenium(웹 브라우저 자동화 도구) ---
from selenium import webdriver  # 실제 웹 브라우저를 제어하는 핵심 도구
from selenium.webdriver.chrome.service import Service  # 크롬 드라이버 서비스를 관리
from selenium.webdriver.chrome.options import Options  # 크롬 브라우저의 옵션(설정)을 제어
from webdriver_manager.chrome import ChromeDriverManager  # 크롬 드라이버를 자동으로 설치 및 관리


# Settings

NAVER_CLIENT_ID = "klkCe1zaN1YXD44JqezW"  # 네이버 API ID
NAVER_CLIENT_SECRET = "2E8To4pAYj"  # 네이버 API Secret
SEARCH_KEYWORD = "삼성"  # 검색할 키워드
ARTICLES_TO_FETCH = 15  # 네이버 API를 통해 한 번에 가져올 기사 수 (최대 100)
BASE_FILENAME = f"{SEARCH_KEYWORD}_뉴스_결과"  # 저장될 파일의 기본 이름
CSV_FILENAME = f"{BASE_FILENAME}.csv"  # 최종적으로 저장될 CSV 파일 이름

# Settings Details
# 병렬 처리할 프로세스 수
PROCESS_COUNT = cpu_count() - 1 if cpu_count() > 1 else 1
# 스크래핑 실패 시 재시도할 횟수
MAX_RETRIES = 2
# 재시도하기 전 대기할 시간 (초)
RETRY_DELAY = 3
# 본문이 잘렸는지 확인하기 위한 키워드 목록
PARTIAL_CONTENT_KEYWORDS = ['더보기', '기사 전체 보기', '로그인', '유료 회원', '구독', '전문']


# 맞춤 로직 - newspaper3k로 잘 안되는 사이트를 위한 특별 규칙 => 추후 추가 해야함!
def parse_kbs_news(soup):
    """KBS 사이트 전용 파서: 'div.view-con' 영역에서 본문을 추출합니다."""
    content = soup.select_one('div.view-con')
    return content.get_text(strip=True) if content else None

def generic_parser(html_content, url):
    """기본 파서: newspaper3k를 사용해 제목, 본문, 날짜를 추출합니다."""
    article = Article(url, language='ko')
    article.set_html(html_content)  # Selenium으로 가져온 HTML 코드를 기사 객체에 설정
    article.parse()  # HTML 코드 분석
    return article.text, article.title, article.publish_date

# 특정 언론사(host)와 그에 맞는 맞춤 파서(함수)를 연결해주는 딕셔너리
SPIDER_RULES = {
    'news.kbs.co.kr': parse_kbs_news,
}


# Main Function

def fetch_naver_news_links(query, display):
    """네이버 뉴스 검색 API를 호출하여 기사 원문 링크 목록을 가져옵니다."""
    print("네이버 뉴스 API를 통해 기사 링크를 수집합니다...")
    api_url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP 오류 발생 시 예외를 일으킴
        items = response.json().get('items', [])
        results = []
        for i, item in enumerate(items):
            link = item.get('originallink') or item.get('link', '')  # 원문 링크를 우선적으로 사용
            host = link.split('/')[2] if link.startswith('http') else "알 수 없음"  # 링크에서 언론사 호스트 추출
            results.append({
                'id': i,  # 각 기사의 고유 번호 (작업자 구분을 위함)
                'link': link,
                'host': host,
                'press': host.replace('www.', ''),
                'pubDate': item.get('pubDate', '')
            })
        print(f"총 {len(results)}개의 기사 링크 수집 완료.")
        return results
    except requests.exceptions.RequestException as e:
        print(f"오류: 네이버 API 요청 실패 - {e}")
        return []

def check_for_partial_content(text):
    """스크래핑한 본문 내용이 일부 잘렸는지 키워드 기반으로 확인합니다."""
    last_portion = text[-200:]  # 효율성을 위해 본문 마지막 200자만 검사
    for keyword in PARTIAL_CONTENT_KEYWORDS:
        if keyword in last_portion:
            return f"본문 잘림 의심 ('{keyword}' 키워드 발견)"
    return "정상"

def scrape_article_worker(news_info):
    """
    [핵심] 개별 기사 하나를 스크래핑하는 '일꾼(Worker)' 함수입니다.
    이 함수가 여러 프로세스에서 동시에 실행됩니다.
    """
    url = news_info['link']
    print(f"[Worker {news_info['id']}] 시작: {url}")

    driver = None
    #안정성을 위한 재시도 로직
    for attempt in range(MAX_RETRIES):
        try:
            # === 각 프로세스는 자신만의 독립적인 웹 드라이버(브라우저)를 설정하고 실행합니다. ===
            options = Options()
            options.add_argument("--headless")  # 브라우저 창을 눈에 보이지 않게 실행
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(20)  # 페이지 로딩 시간이 20초를 넘으면 타임아웃 오류 발생

            # === 실제 웹 스크래핑 수행 ===
            driver.get(url)  # Selenium을 이용해 웹 페이지 접속 (자바스크립트 실행 완료)
            time.sleep(1.5)  # 동적 콘텐츠(광고, 추가 기사 등)가 로드될 시간을 약간 기다림
            html_content = driver.page_source  # 렌더링이 완료된 최종 HTML 코드를 가져옴

            # === 가져온 HTML 코드를 파싱하여 정보 추출 ===
            host, press, api_pubdate = news_info['host'], news_info['press'], news_info['pubDate']
            title, text = None, None

            if host in SPIDER_RULES:  # 이 언론사를 위한 '맞춤 로직'이 있다면
                print(f"[{press}] 맞춤 로직를 사용합니다.")
                soup = BeautifulSoup(html_content, 'html.parser')
                text = SPIDER_RULES[host](soup)  # 해당 맞춤 함수로 본문 파싱
                _, title, _ = generic_parser(html_content, url) # 제목 등은 newspaper3k로 보조
            else:  # '맞춤 로직'가 없다면
                print(f"[{press}] 기본 만능 로직을 사용합니다.")
                text, title, _ = generic_parser(html_content, url) # newspaper3k로 파싱

            # 파싱 결과가 유효한지 검사
            if not title or not text or len(text) < 50:
                raise ValueError("제목 또는 본문 파싱 실패 (내용이 너무 짧음)")

            # === 날짜 정보 처리 ===
            publish_date_str = "날짜 정보 없음"
            try: # 네이버 API에서 받은 날짜 형식을 파싱
                dt_obj = datetime.strptime(api_pubdate, '%a, %d %b %Y %H:%M:%S %z')
                publish_date_str = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                pass # 파싱 실패 시 그냥 넘어감
            
            # 본문이 잘렸는지 최종 확인
            remarks = check_for_partial_content(text)
            
            print(f"[Worker {news_info['id']}] 성공: {title[:20]}...")
            # 성공 시, 추출한 정보들을 딕셔너리 형태로 반환
            return {"제목": title, "작성일": publish_date_str, "본문": text, "신문사": press, "링크": url, "비고": remarks}

        except Exception as e:
            # 스크래핑 도중 어떤 종류의 오류든 발생했을 경우
            print(f"[Worker {news_info['id']}] 실패 (시도 {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)  # 다음 재시도 전 잠시 대기
            else:
                # 최종적으로 실패한 경우, 실패 정보를 딕셔너리 형태로 반환
                return {"제목": "스크래핑 실패", "작성일": "N/A", "본문": str(e), "신문사": news_info['press'], "링크": url, "비고": "최종 실패"}
        finally:
            # try 블록의 성공/실패 여부와 관계없이 항상 실행되는 코드
            if driver:
                driver.quit()  # 리소스 낭비를 막기 위해 사용한 브라우저 프로세스를 반드시 종료


# Save CSV Function
def save_to_csv(articles, filename):
    if not articles:
        print("저장할 기사가 없습니다.")
        return
    
    # CSV 파일의 헤더 정의
    fieldnames = ['제목', '작성일', '본문', '신문사', '링크', '기업명', '비고']
    
    valid_articles = [article for article in articles if article] # None 값을 제외
    for article in valid_articles:
        # 본문의 줄바꿈, 연속 공백 등을 하나로 합쳐서 깔끔하게 정리
        if "본문" in article:
            article["본문"] = " ".join(article["본문"].split())
        article['기업명'] = SEARCH_KEYWORD

    # CSV 파일 쓰기
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()  # 헤더 쓰기
        writer.writerows(valid_articles)  # 데이터 쓰기
    print(f"총 {len(valid_articles)}개의 기사를 '{filename}' 파일로 저장했습니다.")


# Main
def main():
    start_time = time.time()  # 시작 시간 기록
    
    # 1. 네이버 API를 통해 스크래핑할 기사 링크 목록을 가져옴
    news_links_info = fetch_naver_news_links(SEARCH_KEYWORD, ARTICLES_TO_FETCH)
    if not news_links_info:
        return
    
    # 2. 멀티프로세싱 Pool을 사용하여 병렬로 스크래핑 실행
    print(f"{PROCESS_COUNT}개의 프로세스로 병렬 스크래핑을 시작합니다...")
    with Pool(PROCESS_COUNT) as pool:
        # pool.map 함수가 news_links_info 리스트의 각 항목을 scrape_article_worker 함수에 하나씩 전달하여 실행
        scraped_articles = pool.map(scrape_article_worker, news_links_info)
    
    # 3. 모든 작업이 완료되면 결과를 CSV 파일로 저장
    save_to_csv(scraped_articles, CSV_FILENAME)
    
    end_time = time.time()  # 종료 시간 기록
    print(f"\n총 실행 시간: {end_time - start_time:.2f}초")

# 이 스크립트 파일이 직접 실행되었을 때만 main() 함수를 호출
if __name__ == "__main__":
    main()