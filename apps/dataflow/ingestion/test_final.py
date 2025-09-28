import asyncio
import aiohttp
from newspaper import Article
import os
import csv
from datetime import datetime

# Settings

# --- 네이버 API 정보 ---
NAVER_CLIENT_ID = "klkCe1zaN1YXD44JqezW"
NAVER_CLIENT_SECRET = "2E8To4pAYj"

# --- 검색 및 필터링 설정 ---
# 검색할 키워드
SEARCH_KEYWORD = "삼성"
# API를 통해 한 번에 가져올 기사 수 (최대 100)
ARTICLES_TO_FETCH = 20
# 필터링할 기간 (일 단위) # 현재 비활성화.
FILTER_DAYS = 90

# --- 파일 이름 설정 ---
BASE_FILENAME = f"{SEARCH_KEYWORD}_뉴스_결과"
CSV_FILENAME = f"{BASE_FILENAME}.csv"

# API 요청 및 스크래핑 재시도 횟수
MAX_RETRIES = 3

# Main Function

async def fetch_naver_news_links(session, query, display):
    """
    네이버 뉴스 검색 API를 비동기적으로 호출 -> 기사 링크와 메타데이터를 가져옵니다.
    """
    api_url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    
    print(f"'{query}' 키워드로 네이버 뉴스 API 호출 중...")
    try:
        async with session.get(api_url, headers=headers, timeout=10) as response:
            if response.status == 200:
                data = await response.json()
                items = data.get('items', [])
                results = []
                for item in items:
                    press = "정보 없음" # 기본값 설정
                    try:
                        original_link = item.get('originallink', '')
                        if original_link:
                            # domain 추출 후 'www.' 제거해 언론사 명 정제.
                            press = original_link.split('/')[2].replace('www.', '')
                    except IndexError:
                        press = "파싱 실패"
                    
                    results.append({
                        'link': item.get('link', ''), 
                        'press': press,
                        'pubDate': item.get('pubDate', '')
                        })
                    
                return results

            else:
                print(f"네이버 API 오류: {response.status} - {await response.text()}")
                return []
    except Exception as e:
        print(f"네이버 API 요청 중 예외 발생: {e}")
        return []

async def fetch_and_parse(session, news_info):
    """
    개별 뉴스 URL에 접속하여 제목, 본문, 작성일 등 상세 정보를 비동기적으로 스크래핑합니다.
    """
    url, press, api_pubdate = news_info['link'], news_info['press'], news_info['pubDate']
    
    for retry in range(MAX_RETRIES):
        try:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10) as response:
                html_content = await response.text()

            article = Article(url, language='ko')
            article.download(input_html=html_content)
            article.parse()
            
            if not article.title or not article.text:
                raise ValueError("Newspaper3k parsing failed: empty title or text")
            
            # 1. newspaper3k로 날짜 파싱 시도
            publish_date_obj = article.publish_date

            # 2. 실패시, Naver API가 제공한 pubDate로 파싱 시도 (Fall Back)
            if not publish_date_obj and api_pubdate:
                try:
                    #Naver API pubDate 형식 : 'Web, 27 Sep 2025 19:00:00 +0900'
                    publish_date_obj = datetime.strptime(api_pubdate, '%a, %d %b %Y %H:%M:%S %z')
                except(ValueError, KeyError):
                    publish_date_obj = None
            # 최종 날짜를 문자열로 변환
            publish_date_str = publish_date_obj.strftime('%Y-%m-%d %H:%M:%S') if publish_date_obj else "날짜 정보 없음"

            return {
                "제목": article.title,
                "작성일": publish_date_str,
                "본문": article.text,
                "신문사": press,
                "링크": url,
            }
        except Exception as e:
            if retry < MAX_RETRIES - 1:
                await asyncio.sleep(2)
            else:
                print(f"최종 실패: {url} ({e})")
                return None
    return None

# Save Function

def save_to_csv(articles, filename):
    """스크래핑된 기사 리스트를 CSV 파일로 저장합니다."""
    if not articles:
        print("CSV로 저장할 기사가 없습니다.")
        return
        
    fieldnames = ['제목', '작성일', '본문', '신문사', '링크', '기업명']

    for article in articles:
        if "본문" in article:
            article["본문"] = " ".join(article["본문"].split())

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)
    print(f"총 {len(articles)}개의 기사를 '{filename}' 파일로 저장했습니다.")

# Main

async def main():
    """
    전체 스크래핑 프로세스를 비동기적으로 실행하고 관리하는 메인 함수입니다.
    """
    async with aiohttp.ClientSession() as session:
        news_links_info = await fetch_naver_news_links(session, SEARCH_KEYWORD, ARTICLES_TO_FETCH)
        if not news_links_info:
            print("API를 통해 가져올 뉴스 기사가 없습니다. 키워드나 API 설정을 확인하세요.")
            return

        print(f"\nAPI 검색 완료: 총 {len(news_links_info)}개의 기사 링크를 찾았습니다. 스크래핑을 시작합니다...")
        
        tasks = [fetch_and_parse(session, info) for info in news_links_info]
        scraped_articles_results = await asyncio.gather(*tasks)

    successfully_scraped_articles = [article for article in scraped_articles_results if article]
    print(f"\n스크래핑 완료: 총 {len(successfully_scraped_articles)}개의 기사 내용 추출 성공.")
    
    # === 날짜 필터링 로직 비활성화 (주석 처리) ===
    # print(f"최근 {FILTER_DAYS}일 내 기사 필터링 시작...")
    # date_threshold = datetime.now() - timedelta(days=FILTER_DAYS)
    # articles_in_range = []
    # for article in successfully_scraped_articles:
    #     if article['작성일'] != "날짜 정보 없음":
    #         try:
    #             article_date = datetime.strptime(article['작성일'], '%Y-%m-%d %H:%M:%S')
    #             if article_date >= date_threshold:
    #                 articles_in_range.append(article)
    #         except ValueError:
    #             continue
    # print(f"필터링 완료: {len(articles_in_range)}개의 기사가 최근 {FILTER_DAYS}일 내에 작성되었습니다.")

    # 최종 필터링된 결과를 CSV 파일로만 저장합니다.
    save_to_csv(successfully_scraped_articles, CSV_FILENAME)

if __name__ == "__main__":
    # Windows 환경에서 asyncio 실행 시 발생할 수 있는 이벤트 루프 정책 관련 문제를 방지합니다.
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
