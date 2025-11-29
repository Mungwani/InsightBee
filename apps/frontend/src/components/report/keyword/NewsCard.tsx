import { useNavigate } from "react-router-dom";

interface newsCard {
  article_id: number;
  title: string;
  one_line_summary: string;
  source: string;
  published_at: string;
  // onClick: void;
}

export default function NewsCard({
  article_id,
  title,
  one_line_summary,
  source,
  published_at,
}: newsCard) {
  const navigate = useNavigate();

  const handleClick = () => {
    // ✅ /news/:id 로 이동
    navigate(`/news/${article_id}`);
  };

  return (
    <div className="flex flex-col gap-4 text-black border border-gray-200 rounded-2xl p-[10px]">
      <div className="flex justify-between">
        <div className="w-[80%]"> {title}</div>
        <div>긍정</div>
      </div>

      <div className="text-sm text-gray-400">{one_line_summary}</div>
      <div className="flex justify-between items-center">
        {/* 왼쪽 */}
        <div className="flex gap-2 text-xs">
          <div className="flex gap-1">
            <div>사</div>
            <div>{source}</div>
          </div>
          <div className="flex gap-1">
            <div>진</div>
            <div>{published_at} </div>
          </div>
        </div>
        {/* 오른쪽 버튼 */}
        <div className="flex text-[11px] gap-1">
          <button
            className="w-[70px] h-[30px] !bg-white border border-gray-300 rounded-lg"
            onClick={handleClick} // ✅ 여기!
          >
            기사보기
          </button>
        </div>
      </div>
    </div>
  );
}
