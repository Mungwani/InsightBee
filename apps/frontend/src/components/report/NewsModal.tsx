import NewsCard from "./NewsCard";

export default function NewsModal() {
  return (
    <div>
      <div>
        <div className="flex flex-col gap-4 bg-white text-black border border-gray-200 rounded-2xl p-[10px]">
          <div className="flex justify-between">
            <div className="w-[80%]"> 관련 뉴스</div>
            <div className="flex gap-4 ">
              <select
                className="border border-gray-300 rounded-lg px-2 py-1 text-sm cursor-pointer focus:outline-none focus:ring-1 focus:ring-gray-400"
                defaultValue="전체"
              >
                <option value="전체">전체</option>
                <option value="긍정">긍정</option>
                <option value="부정">부정</option>
              </select>
              <select
                className="border border-gray-300 rounded-lg px-2 py-1 text-sm cursor-pointer focus:outline-none focus:ring-1 focus:ring-gray-400"
                defaultValue="최신 순"
              >
                <option value="최신 순">최신 순</option>
                <option value="오래된 순">오래된 순</option>
              </select>
            </div>
          </div>
          <div>3개의 기사가 있습니다</div>
          {/* 이 부분 페이지네이션 ㄱㄱ */}
          <div>
            <NewsCard />
            <NewsCard />
            <NewsCard />
          </div>
        </div>
      </div>
    </div>
  );
}
