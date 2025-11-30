import { useState, useMemo } from "react";
import NewsCard from "./NewsCard";

export default function NewsCardList({ newsData, filter, sortOption }: any) {
  const [page, setPage] = useState(1);
  const itemsPerPage = 3;

  // 1) 필터링
  const filteredData = useMemo(() => {
    if (filter === "전체") return newsData;

    // 지금 구조에서는 "긍정/부정" 데이터가 없어서 예시로 title 기반 필터
    return newsData.filter((item: any) => item.sentiment === filter);
  }, [newsData, filter]);

  // 2) 정렬
  const sortedData = useMemo(() => {
    return [...filteredData].sort((a: any, b: any) => {
      const dateA = new Date(a.published_at).getTime();
      const dateB = new Date(b.published_at).getTime();

      if (sortOption === "최신 순") return dateB - dateA;
      return dateA - dateB;
    });
  }, [filteredData, sortOption]);

  // 3) 페이지네이션
  const totalPages = Math.ceil(sortedData.length / itemsPerPage);

  const paginatedData = sortedData.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  return (
    <div className="flex flex-col gap-4">
      {/* 카드 목록 */}
      {paginatedData.map((item: any) => (
        <NewsCard
          article_id={item.article_id}
          title={item.title}
          one_line_summary={item.one_line_summary}
          source={item.source}
          published_at={item.published_at}
        />
      ))}

      {/* 페이지네이션 버튼 */}
      {totalPages > 1 && (
        <div className="flex items-center  justify-center gap-2 mt-4">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className=" !bg-customBrown  border rounded disabled:opacity-40 !text-xs text-[black]"
          >
            이전
          </button>

          <span className="text-sm">
            {page} / {totalPages}
          </span>

          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className=" !bg-customBrown  border rounded disabled:opacity-40 !text-xs text-[black]"
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}
