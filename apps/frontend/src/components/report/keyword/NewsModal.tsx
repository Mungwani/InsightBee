import { useState } from "react";
import NewsCardList from "./NewsCardList";

export default function NewsModal({ newsData }: any) {
  const [filter, setFilter] = useState("전체");
  const [sortOption, setSortOption] = useState("최신 순");

  return (
    <div>
      <div className="flex flex-col gap-4 bg-white text-black border border-gray-200 rounded-2xl p-[10px]">
        <div className="flex justify-between">
          <div className="w-[80%]">관련 뉴스</div>

          <div className="flex gap-4">
            {/* 필터 */}
            <select
              className="border border-gray-300 rounded-lg px-2 py-1 text-sm"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="전체">전체</option>
              <option value="긍정">긍정</option>
              <option value="부정">부정</option>
            </select>

            {/* 정렬 */}
            <select
              className="border border-gray-300 rounded-lg px-2 py-1 text-sm"
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value)}
            >
              <option value="최신 순">최신 순</option>
              <option value="오래된 순">오래된 순</option>
            </select>
          </div>
        </div>

        <div>{newsData.length}개의 기사가 있습니다</div>

        {/* NewsCardList: 정렬/필터 전달 */}
        <NewsCardList
          newsData={newsData}
          filter={filter}
          sortOption={sortOption}
        />
      </div>
    </div>
  );
}
