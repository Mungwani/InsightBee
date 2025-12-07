/* eslint-disable @typescript-eslint/no-explicit-any */

import NewsModal from "../keyword/NewsModal";

export default function News({ newsData }: any) {
  const allNews = newsData.keyword_groups.flatMap((group: any) =>
    group.news_items.map((news: any) => ({
      ...news,
      keyword: group.keyword,
    }))
  );

  return (
    <div className="flex flex-col gap-4">
      <div className={`flex flex-col transition-all duration-300 `}>
        <div className="relative m:pl-6 animate-fadeIn">
          <div className="bg-gray-50 rounded-2xl p-2 sm:p-4 border border-gray-100 shadow-inner">
            <NewsModal newsData={allNews} newsType="all" />
          </div>
        </div>
      </div>
    </div>
  );
}
