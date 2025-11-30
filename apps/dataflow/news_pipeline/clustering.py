# apps/dataflow/news_pipeline/clustering.py
import logging
import pandas as pd
import numpy as np
from sqlalchemy import text
from sentence_transformers import SentenceTransformer, util
from apps.dataflow.common.db_sa import async_engine

# 동기(Sync) 함수: 실제 데이터 분석 및 클러스터링 수행
def _perform_clustering_logic(df: pd.DataFrame):
    """
    Pandas DataFrame을 받아 AI 유사도 분석 후, 
    업데이트할 기사 ID 목록(대표/중복)을 반환합니다.
    """
    if df.empty or len(df) < 2:
        return []

    # 1. 임베딩 생성 (CPU/GPU 작업)
    # (매번 로드하면 느리므로, 실제 운영 시에는 모델을 전역 로드하거나 별도 서버로 분리 권장)
    model = SentenceTransformer("distiluse-base-multilingual-cased-v1")
    embeddings = model.encode(df["content"].tolist())

    # 2. 클러스터링 (유사도 80% 이상)
    # min_community_size=2: 최소 2개 이상 묶여야 클러스터로 인정
    clusters = util.community_detection(embeddings, min_community_size=2, threshold=0.8)

    updates = []
    
    # 3. 결과 정리
    for cluster_id, cluster_indices in enumerate(clusters):
        # cluster_indices: [0, 5, 12] 같은 DataFrame의 행 인덱스 리스트
        
        # 첫 번째 기사를 '대표 기사'로 선정
        rep_idx = cluster_indices[0]
        rep_article_id = df.iloc[rep_idx]['article_id']
        
        updates.append({
            "article_id": int(rep_article_id),
            "cluster_id": cluster_id,
            "is_representative": True
        })

        # 나머지 기사들은 '중복 기사'로 선정 (숨김 처리)
        for dup_idx in cluster_indices[1:]:
            dup_article_id = df.iloc[dup_idx]['article_id']
            updates.append({
                "article_id": int(dup_article_id),
                "cluster_id": cluster_id,
                "is_representative": False # UI 노출 제외
            })
            
    return updates

# 비동기(Async) 래퍼 함수: Main.py에서 호출
async def run_clustering_process():
    logging.info("Starting AI Deduplication (Clustering)...")
    
    async with async_engine.begin() as conn:
        # 1. 아직 클러스터링 되지 않은(cluster_id IS NULL) + 필터 통과한(is_passed_rule=True) 기사 조회
        # (성능을 위해 최근 3일치만 조회하는 조건을 추가할 수도 있음)
        query = text("""
            SELECT article_id, content 
            FROM news_articles 
            WHERE cluster_id IS NULL 
              AND is_passed_rule = true
              AND content IS NOT NULL
        """)
        result = await conn.execute(query)
        rows = result.fetchall()
        
        if not rows:
            logging.info("No new articles to cluster.")
            return

        # Pandas DataFrame 변환
        df = pd.DataFrame(rows, columns=['article_id', 'content'])
        logging.info(f"Loaded {len(df)} articles for clustering.")

        # 2. CPU 집약적인 AI 작업은 별도 실행 (blocking 방지)
        # 데이터가 많으면 여기서 시간이 좀 걸립니다.
        import asyncio
        loop = asyncio.get_running_loop()
        
        # 동기 함수(_perform_clustering_logic)를 별도 스레드에서 실행
        updates = await loop.run_in_executor(None, _perform_clustering_logic, df)
        
        if not updates:
            logging.info("No duplicates found.")
            return

        # 3. DB 업데이트 (Bulk Update)
        logging.info(f"Found {len(updates)} articles involved in duplicates. Updating DB...")
        
        # 임시 테이블이나 CASE WHEN 구문을 쓰기보다, 간단하게 건별 업데이트 쿼리 실행 (또는 executemany)
        # SQLAlchemy async session의 execute는 리스트 파라미터를 지원함
        update_stmt = text("""
            UPDATE news_articles
            SET cluster_id = :cluster_id, is_representative = :is_representative
            WHERE article_id = :article_id
        """)
        
        await conn.execute(update_stmt, updates)
        logging.info("AI Deduplication update complete.")