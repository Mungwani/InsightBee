import { useState } from "react";
import TopicCard from "./TopicCard";
import NewsModal from "./NewsModal";
// import type { WordData } from "../../../public/data/newsData";

// interface TopicCardListProps {
//   words: WordData[];
// }

export default function TopicCardList({ newsData }: any) {
  const [openKeyword, setOpenKeyword] = useState<string | null>(null);

  const toggleCard = (keyword: string) => {
    setOpenKeyword(openKeyword === keyword ? null : keyword);
  };

  return (
    <div className="grid grid-cols-1 gap-3">
      {newsData.keyword_groups.map((group: any) => (
        <div key={group.keyword} className="flex flex-col gap-2">
          <TopicCard
            topic={group.keyword}
            newsLength={group.news_items.length}
            onClick={() => toggleCard(group.keyword)}
          />

          {openKeyword === group.keyword && (
            // <NewsList newsItems={group.news_items} />
            <NewsModal newsData={group.news_items} />
          )}
        </div>
      ))}
    </div>
  );
}
