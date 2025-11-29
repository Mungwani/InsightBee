import os
import warnings
import re
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed 

import google.generativeai as genai
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util


# --- 1. 설정 (Configuration) ---
ORIGINAL_ARTICLE_TABLE = "news_articles" # 원본 기사 테이블 (news_articles)
RESULT_TABLE_NAME = "article_topics" # 결과를 저장할 테이블 (article_topics)

GEMINI_MODEL_NAME = "gemini-2.5-flash"
TOPIC_CATEGORIES = [
    "신사업/M&A", "경영전략/리더십", "해외진출/글로벌 동향", "투자유치/재무", "신제품/서비스 출시",
    "기술개발/R&D", "생산/공급망 관리", "특허/기술인증", "시장동향/트렌드 분석", "경쟁사 동향",
    "정부규제/정책", "인재채용/인재상", "조직문화/인사제도", "임직원 동정/인사", "노사관계/고용이슈",
    "ESG/지속가능경영", "사회공헌/CSR", "소비자보호/분쟁", "파트너십/협력", "대외활동/홍보", "리스크/위기관리"
]
MAX_WORKERS = 5 # 동시 API 호출을 위한 워커 개수


# --- 2. DB & AI 설정 ---
def setup_db_engine() -> Engine:
    """Load DB URL from .env and create SQLAlchemy engine."""
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL is missing in .env.")
    return create_engine(db_url)


def setup_gemini() -> genai.GenerativeModel:
    """Initialize Gemini model after checking API key."""
    warnings.filterwarnings("ignore")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing in .env.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL_NAME)


# --- 3. DB 입출력 함수 ---
def fetch_all_unprocessed_articles(engine: Engine) -> Optional[pd.DataFrame]:
    """
    Fetch all articles from news_articles that are not yet processed in article_topics.
    """
    print(f"\n1단계: '{RESULT_TABLE_NAME}'에 없는 기사 조회 중...")

    try:
        with engine.connect() as conn:
            # SQL: news_articles의 PK(article_id)와 article_topics의 PK(id)를 조인
            query = text(f"""
                SELECT a.*
                FROM {ORIGINAL_ARTICLE_TABLE} a
                LEFT JOIN {RESULT_TABLE_NAME} ar ON a.article_id = ar.id
                WHERE ar.id IS NULL
                ORDER BY a.article_id ASC;
            """)
            df = pd.read_sql_query(query, conn)
            
            # [전처리] 클러스터링 오류 방지: Null 및 공백 content 제거
            df.dropna(subset=["content"], inplace=True)
            df = df[df["content"].astype(str).str.strip() != ""].copy() # 공백 제거
            df.reset_index(drop=True, inplace=True)

            if df.empty:
                print("✅ 처리할 새로운 기사가 없습니다.")
                return None

            print(f"✅ {len(df)}개 기사 로드 완료.")
            return df

    except SQLAlchemyError as e:
        print(f"❌ DB 조회 오류: {e}")
        return None


def insert_analysis_report(engine: Engine, df: pd.DataFrame):
    """
    Final insertion of analyzed DataFrame into the article_topics table.
    """
    print(f"\n4단계: 분석 결과를 '{RESULT_TABLE_NAME}'에 저장 중...")

    try:
        # [DB 스키마 매핑] news_articles 컬럼을 article_topics 스키마에 맞춥니다.
        df_insert = df[[
            "article_id", "company_id", "title", "published_at",
            "content", "url", "search_keyword", "cluster_id",
            "summary", "topic"
        ]].copy()

        # DataFrame 컬럼명을 DB 컬럼명으로 매핑 (article_topics 스키마에 맞춤)
        df_insert.rename(columns={
            "article_id": "id",          # news_articles.article_id -> article_topics.id (PK)
            "company_id": "기업명",      # news_articles.company_id -> article_topics.기업명
            "published_at": "작성일",    # news_articles.published_at -> article_topics.작성일
            "url": "링크",              # news_articles.url -> article_topics.링크
            "search_keyword": "비고"    # news_articles.search_keyword -> article_topics.비고
            # cluster_id, summary, topic, title, content 등은 이름이 같거나 유사
        }, inplace=True)

        with engine.begin() as conn:
            df_insert.to_sql(RESULT_TABLE_NAME, con=conn, if_exists="append", index=False, chunksize=100)

        print(f"✅ {len(df)}개 기사 저장 완료.")

    except SQLAlchemyError as e:
        print(f"❌ DB 저장 오류: {e}")


# --- 4. AI 분석 및 클러스터링 ---
def get_summary_and_topic(content: str, model: genai.GenerativeModel, categories: List[str]) -> Tuple[str, str]:
    """Combines summarization and classification into a single API call."""
    category_list = ", ".join(categories)
    
    # [프롬프트 최적화] 취업준비생 관점의 요약 및 형식 지정
    prompt = (
        f"당신은 취업 준비생의 면접 준비를 돕는 전문 커리어 애널리스트입니다.\n"
        f"다음 뉴스 기사 본문을 읽고, 2가지 임무를 수행해주세요.\n\n"
        f"1. **[의미 요약]**: 이 뉴스가 지원자에게 어떤 의미가 있는지(성장 동력, 위기, 인재상 등)에 초점을 맞춰 2-3문장으로 요약합니다.\n"
        f"2. **[토픽 분류]**: 주어진 '토픽 목록'에서 이 기사의 핵심 주제와 가장 적합한 카테리 하나만을 선택합니다.\n\n"
        f"--- 토픽 목록 ---\n[{category_list}]\n\n"
        f"--- 기사 본문 ---\n{content}\n\n"
        f"--- [매우 중요] 응답 형식 ---\n"
        f"반드시 아래와 같은 형식으로만 응답해야 합니다. (다른 설명 없이):\n"
        f"요약: [여기에 1번 임무의 요약 내용을 작성]\n"
        f"토픽: [여기에 2번 임무의 토픽을 작성]"
    )

    try:
        res = model.generate_content(prompt)
        text = res.text.strip().replace("**", "")

        # 정규식을 이용한 강력한 파싱
        summary = re.search(r"요약:\s*(.*?)(?=\n?토픽:|\Z)", text, re.DOTALL)
        topic = re.search(r"토픽:\s*(.*)", text)

        summary_txt = summary.group(1).strip() if summary else f"요약 파싱 실패: {text[:50]}..."
        topic_txt = topic.group(1).strip() if topic else "분류 실패"
        
        # 목록에 있는 토픽인지 최종 확인
        topic_clean = next((c for c in categories if c in topic_txt), "분류 실패")

        return summary_txt, topic_clean

    except Exception as e:
        return f"API 호출 오류: {e}", "분류 실패"


def cluster_articles(df: pd.DataFrame) -> pd.DataFrame:
    """Clusters articles based on content similarity (80% threshold)."""
    print("\n2단계: 본문 유사도 기반 클러스터링 중...")
    
    if df.empty:
        df["cluster_id"] = np.nan
        return df

    try:
        model = SentenceTransformer("distiluse-base-multilingual-cased-v1")
        
        if len(df) <= 1:
            df["cluster_id"] = -1
            print("⚠️ 기사 수가 1개 이하로 클러스터링을 건너뛰고 모두 고유 기사로 처리합니다.")
            return df
        
        embeddings = model.encode(df["content"].tolist())
        
        if embeddings is None or not isinstance(embeddings, np.ndarray) or embeddings.ndim != 2 or embeddings.shape[0] < 2:
            print("❌ 임베딩 생성 실패 또는 데이터 불충분. 클러스터링을 건너뛸 수 있습니다.")
            df["cluster_id"] = -1
            return df

        # [최종 설정] 중복 제거 기준: 본문 80% 유사도 (threshold=0.8)
        clusters = util.community_detection(embeddings, min_community_size=2, threshold=0.8)
        cluster_map = {doc_id: i for i, cluster in enumerate(clusters) for doc_id in cluster}
        df["cluster_id"] = df.index.map(lambda x: cluster_map.get(x, -1))

        print(f"✅ {len(clusters)}개 클러스터 탐지 완료.")
        return df

    except Exception as e:
        print(f"❌ 클러스터링 오류: {e}. 모든 기사를 고유 기사로 처리합니다.")
        df["cluster_id"] = -1
        return df


# --- 5. 메인 실행 ---
def run_topic_worker():
    """Main worker function to fetch, analyze, and store data in DB."""
    print("--- InsightBee 토픽 분석 배치 실행 ---")

    try:
        engine = setup_db_engine()
        gemini_model = setup_gemini()
    except Exception as e:
        print(f"❌ 초기 설정 실패: {e}")
        return

    df_pending = fetch_all_unprocessed_articles(engine)
    if df_pending is None or df_pending.empty:
        return

    df_clustered = cluster_articles(df_pending)

    # 2-1. 중복 기사 제거 및 대표 기사 선정
    reps = df_clustered[df_clustered["cluster_id"] != -1].drop_duplicates(subset=["cluster_id"], keep="first")
    uniques = df_clustered[df_clustered["cluster_id"] == -1]
    df_target = pd.concat([reps, uniques]).sort_index()

    print(f"✅ 분석 대상 기사 수: {len(df_target)}개")

    # 3. AI 분석 실행 (멀티스레딩)
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(get_summary_and_topic, row["content"], gemini_model, TOPIC_CATEGORIES): row
            for _, row in df_target.iterrows()
        }

        for future in tqdm(as_completed(futures), total=len(df_target), desc="AI 분석 중"):
            row = futures[future]
            try:
                summary, topic = future.result()
            except Exception as e:
                summary, topic = f"API 오류: {e}", "분류 실패"

            row["summary"], row["topic"] = summary, topic
            results.append(row)

    df_final = pd.DataFrame(results)
    
    # 4. 분석 결과 DB 저장
    insert_analysis_report(engine, df_final)
    print("\n 모든 기사 분석 및 저장 완료.")


if __name__ == "__main__":
    run_topic_worker()
