import NewsCard from "./NewsCard";
import WordCloudTest from "./WordCloudTest";

export default function KeywordNews() {
  return (
    <div className="mt-3 space-y-4 px-4   ">
      <section className="bg-white rounded-2xl shadow p-4">
        <div className="flex flex-col gap-2">
          <div className="flex flex-col gap-1">
            <div className="text-black">핵심 키워드</div>
            <div className="text-gray-400 text-xs">
              클릭하면 관련 뉴스를 확인할 수 있습니다
            </div>
          </div>
          <div className=" bg-amber-200">
            <WordCloudTest />
          </div>
        </div>
      </section>
      <section className="bg-white rounded-2xl shadow p-4">
        <div>
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <div className="text-black">토픽별 분석</div>
              <div className="text-gray-400 text-xs">
                AI가 주제별로 분류한 뉴스 토픽들입니다
              </div>
            </div>
            <NewsCard />
            <NewsCard />
            <NewsCard />
            <NewsCard />
          </div>
        </div>
      </section>
    </div>
  );
}
