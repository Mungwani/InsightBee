import os
import re
import warnings
from typing import List, Tuple, Optional
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


# --- 설정 ---
ORIGINAL_ARTICLE_TABLE = "news_articles"
RESULT_TABLE_NAME = "article_topics"

GEMINI_MODEL_NAME = "gemini-2.5-flash"
TOPIC_CATEGORIES = [
    "신사업/M&A", "경영전략/리더십", "해외진출/글로벌 동향", "투자유치/재무", "신제품/서비스 출시",
    "기술개발/R&D", "생산/공급망 관리", "특허/기술인증", "시장동향/트렌드 분석", "경쟁사 동향",
    "정부규제/정책", "인재채용/인재상", "조직문화/인사제도", "임직원 동정/인사", "노사관계/고용이슈",
    "ESG/지속가능경영", "사회공헌/CSR", "소비자보호/분쟁", "파트너십/협력", "대외활동/홍보", "리스크/위기관리"
]
MAX_WORKERS = 5


# --- DB & AI 설정 ---
def setup_db_engine() -> Engine:
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL이 .env에 없습니다.")
    return create_engine(db_url)


def setup_gemini() -> genai.GenerativeModel:
    warnings.filterwarnings("ignore")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY가 .env에 없습니다.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL_NAME)


# --- DB 함수 ---
def fetch_all_unprocessed_articles(engine: Engine) -> Optional[pd.DataFrame]:
    print(f"\n1단계: '{RESULT_TABLE_NAME}'에 없는 기사 조회 중...")

    query = text(f"""
        SELECT a.*
        FROM {ORIGINAL_ARTICLE_TABLE} a
        LEFT JOIN {RESULT_TABLE_NAME} ar ON a.article_id = ar.id
        WHERE ar.id IS NULL
        ORDER BY a.article_id ASC;
    """)

    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
        df.dropna(subset=["content"], inplace=True)
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
    print(f"\n4단계: 분석 결과를 '{RESULT_TABLE_NAME}'에 저장 중...")

    try:
        df_insert = df[[
            "article_id", "company_id", "title", "published_at",
            "content", "url", "search_keyword", "cluster_id",
            "summary", "topic"
        ]].copy()

        df_insert.rename(columns={
            "article_id": "id",
            "company_id": "기업명",
            "published_at": "작성일",
            "url": "링크",
            "search_keyword": "비고"
        }, inplace=True)

        with engine.begin() as conn:
            df_insert.to_sql(RESULT_TABLE_NAME, con=conn, if_exists="append", index=False, chunksize=100)

        print(f"✅ {len(df)}개 기사 저장 완료.")

    except SQLAlchemyError as e:
        print(f"❌ DB 저장 오류: {e}")


# --- AI 분석 ---
def get_summary_and_topic(content: str, model: genai.GenerativeModel, categories: List[str]) -> Tuple[str, str]:
    category_list = ", ".join(categories)
    prompt = (
        f"다음 뉴스 기사 본문을 읽고 두 가지를 수행하세요.\n"
        f"1. 요약: 기사 내용을 2~3문장으로 간결히 요약.\n"
        f"2. 토픽: 아래 목록 중 가장 적합한 하나를 선택.\n\n"
        f"[토픽 목록]\n{category_list}\n\n"
        f"[본문]\n{content}\n\n"
        f"---응답 형식---\n"
        f"요약: ...\n토픽: ..."
    )

    try:
        res = model.generate_content(prompt)
        text = res.text.strip().replace("**", "")

        summary = re.search(r"요약:\s*(.*?)(?=\n?토픽:|\Z)", text, re.DOTALL)
        topic = re.search(r"토픽:\s*(.*)", text)

        summary_txt = summary.group(1).strip() if summary else "요약 실패"
        topic_txt = topic.group(1).strip() if topic else "분류 실패"
        topic_clean = next((c for c in categories if c in topic_txt), "분류 실패")

        return summary_txt, topic_clean

    except Exception as e:
        return f"요약 오류: {e}", "분류 실패"


# --- 클러스터링 ---
def cluster_articles(df: pd.DataFrame) -> pd.DataFrame:
    print("\n2단계: 본문 유사도 기반 클러스터링 중...")
    if df.empty:
        df["cluster_id"] = np.nan
        return df

    try:
        model = SentenceTransformer("distiluse-base-multilingual-cased-v1")
        embeddings = model.encode(df["content"].tolist())
        clusters = util.community_detection(embeddings, min_community_size=2, threshold=0.8)
        cluster_map = {doc_id: i for i, cluster in enumerate(clusters) for doc_id in cluster}
        df["cluster_id"] = df.index.map(lambda x: cluster_map.get(x, -1))

        print(f"✅ {len(clusters)}개 클러스터 탐지 완료.")
        return df

    except Exception as e:
        print(f"❌ 클러스터링 오류: {e}")
        df["cluster_id"] = -1
        return df


# --- 메인 ---
def run_topic_worker():
    print("--- InsightBee 토픽 분석 시작 ---")

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

    reps = df_clustered[df_clustered["cluster_id"] != -1].drop_duplicates(subset=["cluster_id"], keep="first")
    uniques = df_clustered[df_clustered["cluster_id"] == -1]
    df_target = pd.concat([reps, uniques]).sort_index()

    print(f"✅ 분석 대상 기사 수: {len(df_target)}개")

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
    insert_analysis_report(engine, df_final)
    print("\n🎉 모든 기사 분석 및 저장 완료.")


if __name__ == "__main__":
    run_topic_worker()
