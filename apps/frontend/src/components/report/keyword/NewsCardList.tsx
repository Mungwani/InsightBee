/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useMemo, useEffect } from "react";
import NewsCard from "./NewsCard";
import { ChevronLeft, ChevronRight, SearchX } from "lucide-react";

export default function NewsCardList({ newsData, filter, sortOption }: any) {
  const [page, setPage] = useState(1);
  const itemsPerPage = 3;

  const filteredData = useMemo(() => {
    if (filter === "전체") return newsData;
    return newsData.filter((item: any) => item.sentiment === filter);
  }, [newsData, filter]);

  const sortedData = useMemo(() => {
    return [...filteredData].sort((a: any, b: any) => {
      const dateA = new Date(a.published_at).getTime();
      const dateB = new Date(b.published_at).getTime();

      if (sortOption === "최신 순") return dateB - dateA;
      return dateA - dateB;
    });
  }, [filteredData, sortOption]);

  useEffect(() => {
    setPage(1);
  }, [filter, sortOption]);

  const totalPages = Math.ceil(sortedData.length / itemsPerPage);
  const paginatedData = sortedData.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  if (sortedData.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-16 h-16 bg-[#FFF3E0] rounded-full flex items-center justify-center mb-4">
          <SearchX className="w-8 h-8 text-[#FFA000]" />
        </div>
        <p className="text-gray-500 font-medium">해당 조건의 뉴스가 없습니다.</p>
        <p className="text-xs text-gray-400 mt-1">필터를 변경하여 다시 검색해보세요.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-4 min-h-[300px]">
        {paginatedData.map((item: any) => (
          <NewsCard
            key={item.article_id}
            article_id={item.article_id}
            title={item.title}
            one_line_summary={item.one_line_summary}
            source={item.source}
            published_at={item.published_at}
          />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 mt-2 mb-4">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            className="p-2 rounded-full text-gray-400 hover:bg-[#FFF3E0] hover:text-[#4F200D] disabled:opacity-30 disabled:hover:bg-transparent transition-colors duration-200"
            aria-label="이전 페이지"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          <span className="text-sm font-medium text-gray-600">
            <span className="text-[#4F200D] font-bold text-base">{page}</span>
            <span className="mx-2 text-gray-300">/</span>
            {totalPages}
          </span>

          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            className="p-2 rounded-full text-gray-400 hover:bg-[#FFF3E0] hover:text-[#4F200D] disabled:opacity-30 disabled:hover:bg-transparent transition-colors duration-200"
            aria-label="다음 페이지"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>
      )}
    </div>
  );
}