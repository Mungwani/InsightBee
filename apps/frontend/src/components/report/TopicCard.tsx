import HashTag from "./HashTag";

interface TopicCard {
  title: string;
  newsLength: number;
  description: string;
  onClick: void;
}
export default function TopicCard({ topic, newsLength, onClick }: any) {
  return (
    <div
      onClick={onClick}
      className="flex flex-col gap-4 text-black border border-gray-200 rounded-2xl p-[10px]"
    >
      <div className="flex justify-between">
        <div className="w-[80%]">{topic}</div>
        {/* <div>{word.sentiment === "positive" ? "긍정" : "부정"}</div> */}
      </div>

      {/* <div className="text-sm text-gray-400">{data.description}</div> */}
      <button className="!bg-white text-gray-400 !text-xs w-[80px] !p-0">
        📄 {newsLength}개 기사
      </button>
      {/* <HashTag /> */}
      {/* <div>
        <div>뉴스 기사 보기</div>
      </div> */}
    </div>
  );
}
