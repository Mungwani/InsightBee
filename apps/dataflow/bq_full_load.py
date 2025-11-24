import asyncio
from datetime import datetime, timezone

from sqlalchemy import text

from google.cloud import bigquery

from apps.dataflow.common.db_sa import async_engine
from apps.dataflow import config 


async def fetch_all_articles() -> list[dict]:
    """Cloud SQL(Postgres)에서 news_articles 전체를 가져오는 비동기 함수."""
    async with async_engine.connect() as conn: 
        result = await conn.execute(
            text(
                """
                SELECT
                  article_id,
                  company_id,
                  title,
                  url,
                  url_hash,
                  content,
                  published_at,
                  search_keyword,
                  score,
                  matched_keywords,
                  is_passed_rule,
                  updated_at
                FROM news_articles
                """
            )
        )
        rows = result.mappings().all()  # Row -> dict-like
        return [dict(row) for row in rows]


async def run_full_load() -> None:
    # 1) Postgres에서 전체 기사 읽기
    rows = await fetch_all_articles()
    print(f"[FULL LOAD] fetched {len(rows)} rows from Cloud SQL")

    # 2) BigQuery 클라이언트
    client = bigquery.Client(project=config.BQ_PROJECT)
    table_id = f"{config.BQ_PROJECT}.{config.BQ_DATASET}.{config.BQ_TABLE}"

    ingested_at = datetime.now(timezone.utc)

    # 3) BigQuery에 넣을 형태로 가공
    bq_rows = []
    for r in rows:
        published_at = r["published_at"]
        updated_at = r["updated_at"]

        bq_rows.append(
            {
                "article_id":       r["article_id"],
                "company_id":       r["company_id"],
                "title":            r["title"],
                "url":              r["url"],
                "url_hash":         r["url_hash"],
                "content":          r["content"],
                "published_at":     published_at.isoformat() if published_at else None,
                "search_keyword":   r["search_keyword"],
                "score":            r["score"],
                "matched_keywords": r["matched_keywords"],
                "is_passed_rule" :  r["is_passed_rule"],
                "updated_at":       updated_at.isoformat() if published_at else None,
                "ingested_at":      ingested_at.isoformat()
            }
        )

    # 4) BigQuery로 적재 (WRITE_TRUNCATE → full load)
    job = client.load_table_from_json(
        json_rows= bq_rows,
        destination=table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"),
    )
    job.result()
    print(f"[FULL LOAD] loaded {len(bq_rows)} rows into {table_id}")

    # 5) AsyncEngine 정리
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_full_load())
