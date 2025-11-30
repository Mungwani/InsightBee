# config.py
# 비밀 키, DB 정보, API 키, 고정 설정값 등
import os
from dotenv import load_dotenv

load_dotenv()


# --- Naver API 인증 키 ---
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# --- Cloud SQL 접속 정보 ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET_ID = os.getenv("BIGQUERY_DATASET_ID")
TABLE_NEWS_RAW = os.getenv("TABLE_NEWS_RAW")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
  raise ValueError("DB 접속 환경 변수가 설정되지 않았습니다.")

DB_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# --- 스크래핑 정책 ---
ARTICLES_PER_PAGE = 100
TARGET_ARTICLES_PER_COMPANY = 300 
REQUEST_TIMEOUT = 20

# --- 동시성 제어 ---
CONCURRENT_REQUESTS_LINKS = 2
CONCURRENT_REQUESTS_SCRAPE_FAST = 50 
CONCURRENT_SELENIUM_TASKS = 1  

# --- 언론사 및 사이트 분류 ---
ALLOWED_PRESS_HOSTS = {
    'chosun.com', 'joongang.co.kr', 'donga.com', 'hani.co.kr', 'khan.co.kr', 'seoul.co.kr', 'kmib.co.kr', 'munhwa.com', 'segye.com', 'hankookilbo.com', 'news.kbs.or.kr', 'imnews.imbc.com', 'news.sbs.co.kr', 'ytn.co.kr', 'yonhapnewstv.co.kr', 'jtbc.co.kr', 'ichannela.com', 'mbn.co.kr', 'tvchosun.com', 'yna.co.kr', 'newsis.com', 'news1.kr', 'hankyung.com', 'mk.co.kr', 'edaily.co.kr', 'asiae.co.kr', 'wowtv.co.kr', 'fnnews.com', 'sedaily.co.kr', 'heraldcorp.com', 'moneys.co.kr', 'sentv.co.kr', 'etoday.co.kr', 'zdnet.co.kr', 'etnews.co.kr', 'ddaily.co.kr', 'inews24.com', 'bloter.net', 'dt.co.kr', 'ciokorea.com', 'it.chosun.com',
}
JAVASCRIPT_REQUIRED_SITES = {'imnews.imbc.com', 'news.sbs.co.kr', 'jtbc.co.kr'}
SPIDER_RULES = {'chosun.com': 'section.article-body',
                'news.sbs.co.kr': 'div.text_area',
                'jtbc.co.kr': 'div.article_content',
                'joongang.co.kr': 'div#article_body',
                'donga.com': 'div.article_view',
                'hani.co.kr': 'div.article-text-font-size', # 한겨레
                'khan.co.kr': 'div.art_body',             # 경향신문
                'seoul.co.kr': 'div#articleContent',        # 서울신문
                'kmib.co.kr': 'div#article_body',           # 국민일보
                'munhwa.com': 'div#news_body',              # 문화일보
                'segye.com': 'div.news_img_wrap',           # 세계일보
                'hankookilbo.com': 'div.article-body',      # 한국일보
                # (방송사)
                'news.kbs.or.kr': 'div#cont_newstext',
                'ytn.co.kr': 'div.content',
                'yonhapnewstv.co.kr': 'div.article-text',
                'ichannela.com': 'div.article-body',        # 채널A
                'mbn.co.kr': 'div.news_content_text',
                'tvchosun.com': 'div.article_body_content', # (news.tvchosun.com)

                # (통신사)
                'yna.co.kr': 'article.story-content',       # 연합뉴스
                'newsis.com': 'div#articleBody',
                'news1.kr': 'div#articles_detail',

                # (경제/IT지)
                'hankyung.com': 'div#article-body',         # 한국경제
                'mk.co.kr': 'div.art_txt',                  # 매일경제
                'edaily.co.kr': 'div.article_body',
                'asiae.co.kr': 'div.article_view',          # 아시아경제
                'wowtv.co.kr': 'div#viewContent',
                'fnnews.com': 'div#article_content',
                'sedaily.co.kr': 'div.article_con',         # 서울경제
                'heraldcorp.com': 'div#articleText',      # 헤럴드경제
                'moneys.co.kr': 'div#article-view-content-div',
                'sentv.co.kr': 'div#article-content',
                'etoday.co.kr': 'div.articleView',
                'zdnet.co.kr': 'div.view_page',
                'etnews.co.kr': 'div.article_body',         # 전자신문
                'ddaily.co.kr': 'div#article_body',
                'inews24.com': 'div#article_body',
                'bloter.net': 'div.article--content',
                'dt.co.kr': 'div.article_view',
                'ciokorea.com': 'div.node_body',
                'it.chosun.com': 'section.article-body',
}