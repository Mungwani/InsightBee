/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import NewsCardList from "./NewsCardList";
import { Filter, ArrowUpDown, ChevronDown, Newspaper } from "lucide-react";

export default function NewsModal({ newsData, newsType }: any) {
  const [filter, setFilter] = useState("전체");
  const [sortOption, setSortOption] = useState("최신 순");

  return (
    <div className="flex flex-col w-full h-full mt-5">
      <div className="flex flex-row justify-between items-end mb-3">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-gray-100 rounded-lg">
              <Newspaper className="w-4 h-4 text-gray-700" />
            </div>
            <h2 className="text-m font-bold text-gray-900 leading-none">
              관련 뉴스
            </h2>
          </div>

          <p className="text-xs text-gray-500 font-medium pl-[38px]">
            분석된 기사{" "}
            <span className="text-[#4F200D] font-bold">
              {newsData?.length || 0}
            </span>
            건
          </p>
        </div>
      </div>

      <div className="flex gap-2 ml-auto mb-2 mr-1">
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

      <div className="flex-1 min-h-0">
        <NewsCardList
          newsData={newsData || []}
          filter={filter}
          sortOption={sortOption}
          newsType={newsType}
        />
      </div>
    </div>
  );
}
