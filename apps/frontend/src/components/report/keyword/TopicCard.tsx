import { FileText, Hash } from "lucide-react";

interface TopicCardProps {
  topic: string;
  newsLength: number;
  onClick: () => void;
  isOpen?: boolean;
}

export default function TopicCard({ topic, newsLength, onClick, isOpen }: TopicCardProps) {
  return (
    <button
      onClick={onClick}
      className={`group w-full flex justify-between items-center rounded-2xl p-5 transition-all duration-200 border
        ${isOpen
          ? "bg-[#FFFBF2] border-[#FFA000] shadow-md"
          : "bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300"
        }
      `}
    >
      {/* 왼쪽: 해시태그 + 텍스트 */}
      <div className="flex items-center gap-3">
        <div
          className={`flex items-center justify-center w-9 h-9 rounded-full transition-colors duration-200
            ${isOpen
              ? "bg-[#FFA000] text-white"
              : "bg-[#F3F3F3] text-gray-400 group-hover:text-gray-900 group-hover:bg-gray-200"
            }
          `}
        >
          <Hash className="w-4 h-4" />
        </div>

        <div className="text-left">
          <span
            className={`block text-base font-bold tracking-wide transition-colors duration-200
              ${isOpen
                ? "text-[#4F200D]"
                : "text-gray-400 group-hover:text-gray-900"
              }
            `}
          >
            {topic}
          </span>
        </div>
      </div>

      {/* 오른쪽: 기사 개수 뱃지 */}
      <div className="flex items-center gap-3">
        <div
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all duration-200
            ${isOpen
              ? "bg-white text-[#FFA000] font-bold border border-[#FFA000]/20"
              : "bg-gray-100 text-gray-600 border border-transparent group-hover:bg-gray-200 group-hover:text-gray-800"
            }
          `}
        >
          <FileText className="w-3.5 h-3.5" />
          <span className="text-xs">{newsLength}건</span>
        </div>
      </div>
    </button>
  );
}