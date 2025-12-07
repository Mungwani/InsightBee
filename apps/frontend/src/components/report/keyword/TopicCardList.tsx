/* eslint-disable @typescript-eslint/no-explicit-any */

import { useState } from "react";
import TopicCard from "./TopicCard";
import NewsModal from "./NewsModal";

export default function TopicCardList({ newsData }: any) {
  const [openKeyword, setOpenKeyword] = useState<string | null>(null);

  const toggleCard = (keyword: string) => {
    setOpenKeyword(openKeyword === keyword ? null : keyword);
  };

  return (
    <div className="flex flex-col gap-4">
      {newsData.keyword_groups.map((group: any) => {
        const isOpen = openKeyword === group.keyword;

        return (
          <div
            key={group.keyword}
            className={`flex flex-col transition-all duration-300 ${isOpen ? "gap-3" : "gap-0"
              }`}
          >
            {/* 1. 토픽 카드 */}
            <div className="relative z-10">
              <TopicCard
                topic={group.keyword}
                newsLength={group.news_items.length}
                onClick={() => toggleCard(group.keyword)}
                isOpen={isOpen}
              />
            </div>

            {/* 2. 확장 영역 */}
            {isOpen && (
              <div className="relative m:pl-6 animate-fadeIn">
                <div className="bg-gray-50 rounded-2xl p-2 sm:p-4 border border-gray-100 shadow-inner">
                  <NewsModal newsData={group.news_items} newsType="topic" />
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
