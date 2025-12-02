import { useNavigate } from "react-router-dom";
import { CalendarDays, Newspaper, ChevronRight } from "lucide-react";

interface NewsCardProps {
  article_id: number;
  title: string;
  one_line_summary: string;
  source: string;
  published_at: string;
}

export default function NewsCard({
  article_id,
  title,
  one_line_summary,
  source,
  published_at,
}: NewsCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/news/${article_id}`);
  };

  // ✅ 날짜 포맷팅 함수 (YYYY.MM.DD)
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (e) {
      return dateString; // 에러나면 원래 문자열 반환
    }
  };

  return (
    <div
      onClick={handleClick}
      className="flex flex-col gap-3 bg-white border border-gray-100 rounded-2xl p-5 shadow-sm hover:shadow-md hover:border-[#D7CCC8] transition-all duration-200 cursor-pointer group"
    >
      {/* 상단: 타이틀 */}
      <div className="flex justify-between items-start gap-2">
        <h4 className="text-[16px] font-bold text-gray-800 leading-snug group-hover:text-[#4F200D] transition-colors">
          {title}
        </h4>
      </div>

      {/* 중간: 요약 */}
      <p className="text-sm text-gray-500 line-clamp-2 leading-relaxed">
        {one_line_summary}
      </p>

      {/* 하단: 정보 및 날짜 */}
      <div className="flex justify-between items-end mt-1 pt-3 border-t border-gray-50">
        <div className="flex flex-col gap-1.5">
          {/* 언론사 */}
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <Newspaper className="w-3.5 h-3.5" />
            <span className="font-medium">{source}</span>
          </div>
          {/* 날짜 */}
          <div className="flex items-center gap-1.5 text-xs text-gray-400">
            <CalendarDays className="w-3.5 h-3.5" />
            <span>{formatDate(published_at)}</span>
          </div>
        </div>

        {/* '기사보기' 버튼 */}
        <button
          className="flex items-center gap-1 pl-3 pr-2 py-1.5 rounded-lg text-xs font-semibold text-gray-600 bg-gray-100 group-hover:bg-[#4F200D] group-hover:text-white transition-colors duration-200"
        >
          기사보기
          <ChevronRight className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
}