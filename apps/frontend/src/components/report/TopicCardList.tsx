import TopicCard from "./TopicCard";
import type { WordData } from "../../../public/data/newsData";

interface TopicCardListProps {
  words: WordData[];
}

export default function TopicCardList({ words }: TopicCardListProps) {
  return (
    <div className="grid grid-cols-1 gap-3">
      {words.map((word) => (
        <TopicCard key={word.text} word={word} />
      ))}
    </div>
  );
}
