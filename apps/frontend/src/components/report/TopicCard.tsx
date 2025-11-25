import HashTag from "./HashTag";
import type { WordData } from "../../../public/data/newsData";

interface TopicCardProps {
  word: WordData;
}

export default function TopicCard({ word }: TopicCardProps) {
  return (
    <div className="flex flex-col gap-4 text-black border border-gray-200 rounded-2xl p-[10px]">
      <div className="flex justify-between">
        <div className="w-[80%]">"{word.text}" 관련 뉴스</div>
        <div>{word.sentiment === "positive" ? "긍정" : "부정"}</div>
      </div>

      <div className="text-sm text-gray-400">{word.description}</div>
      <button className="!bg-white text-gray-400 !text-xs w-[80px] !p-0">
        📄 {word.news}개 기사
      </button>
      <HashTag />
      <div>
        <div>뉴스 기사 보기</div>
      </div>
    </div>
  );
}
