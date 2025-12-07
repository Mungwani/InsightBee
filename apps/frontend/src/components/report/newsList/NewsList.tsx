import { Layers, FileWarning } from "lucide-react";
import News from "./News";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function NewsList({ newsData }: any) {
  // 데이터가 없을 때 예쁜 Empty State 보여주기
  if (!newsData) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-400">
        <FileWarning className="w-10 h-10 mb-2 opacity-50" />
        <p className="text-sm">분석할 뉴스 데이터가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="mt-4 px-4 pb-10 space-y-5">
      {/* 토픽별 분석 */}
      <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        {/* 헤더 영역 */}
        <div className="mb-5">
          <div className="flex items-center gap-2 mb-1">
            {/* 아이콘: 토픽/레이어 의미의 Layers 사용 */}
            <Layers className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-bold text-gray-800">토픽별 분석</h3>
          </div>
          <p className="text-xs text-gray-400 pl-7">
            AI가 주제별로 분류한 뉴스 토픽들을 확인해보세요.
          </p>
        </div>

        {/* 컨텐츠 영역 */}
        <div>
          <News newsData={newsData} />
        </div>
      </section>
    </div>
  );
}
