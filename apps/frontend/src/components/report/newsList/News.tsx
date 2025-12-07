//components/newsList/News.tsx

/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import { FileWarning, Newspaper, Filter, ArrowUpDown, ChevronDown } from "lucide-react";
import NewsCardList from "../keyword/NewsCardList";

export default function News({ newsData }: any) {
  const [filter, setFilter] = useState("전체");
  const [sortOption, setSortOption] = useState("최신 순");

  if (!newsData || !newsData.keyword_groups || newsData.keyword_groups.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-400">
        <FileWarning className="w-10 h-10 mb-2 opacity-50" />
        <p className="text-sm">분석할 뉴스 데이터가 없습니다.</p>
      </div>
    );
  }

  const allNews = newsData.keyword_groups.flatMap((group: any) =>
    group.news_items.map((news: any) => ({
      ...news,
      keyword: group.keyword,
    }))
  );

  const newsCount = allNews?.length || 0;

  return (
    <div className="mt-4 px-4 pb-10 space-y-5">
      <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">

        {/* 헤더 및 필터 영역 (수직 배치) */}
        <div className="mb-5 flex flex-col gap-3">

          {/* 1. 제목 및 분석된 기사 수 (상단 영역) */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2 mb-1">
              <Newspaper className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-bold text-gray-800">전체 뉴스 목록</h3>
            </div>
            <p className="text-xs text-gray-500 font-medium pl-7 mt-1">
              분석된 기사{" "}
              <span className="text-[#4F200D] font-bold">
                {newsCount}
              </span>
              건
            </p>
          </div>

          {/* 2. 필터 및 정렬 드롭다운 (하단 영역, 우측 정렬) */}
          <div className="flex gap-2 ml-auto"> {/* ml-auto를 사용하여 우측으로 밀어냅니다. */}
            {/* 필터 Select */}
            <div className="relative">
              <div className="absolute left-2 top-1/2 -translate-y-1/2 pointer-events-none z-10">
                <Filter className="w-3 h-3 text-gray-500" />
              </div>
              <select
                className="appearance-none bg-white border border-gray-300 rounded-md pl-7 pr-6 py-1 text-xs text-gray-700 focus:outline-none focus:border-[#4F200D] transition-colors cursor-pointer shadow-sm hover:bg-gray-50"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="전체">전체</option>
                <option value="긍정">긍정</option>
                <option value="부정">부정</option>
                <option value="중립">중립</option>
              </select>
              <div className="absolute right-1.5 top-1/2 -translate-y-1/2 pointer-events-none z-10">
                <ChevronDown className="w-3 h-3 text-gray-400" />
              </div>
            </div>

            {/* 정렬 Select */}
            <div className="relative">
              <div className="absolute left-2 top-1/2 -translate-y-1/2 pointer-events-none z-10">
                <ArrowUpDown className="w-3 h-3 text-gray-500" />
              </div>
              <select
                className="appearance-none bg-white border border-gray-300 rounded-md pl-7 pr-6 py-1 text-xs text-gray-700 focus:outline-none focus:border-[#4F200D] transition-colors cursor-pointer shadow-sm hover:bg-gray-50"
                value={sortOption}
                onChange={(e) => setSortOption(e.target.value)}
              >
                <option value="최신 순">최신순</option>
                <option value="오래된 순">과거순</option>
              </select>
              <div className="absolute right-1.5 top-1/2 -translate-y-1/2 pointer-events-none z-10">
                <ChevronDown className="w-3 h-3 text-gray-400" />
              </div>
            </div>
          </div>
        </div>

        {/* 뉴스 카드 목록 */}
        <div className="animate-fadeIn">
          <NewsCardList
            newsData={allNews || []}
            filter={filter}
            sortOption={sortOption}
            newsType="all"
          />
        </div>
      </section>
    </div>
  );
}