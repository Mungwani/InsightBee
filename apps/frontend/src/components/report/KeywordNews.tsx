import NewsCardList from "./TopicCardList";
import WordCloud from "./wordCloud";
import { sentimentWords } from "../../../public/data/newsData"; // 워드 클라우드 글자 데이터
export default function KeywordNews() {
  // value가 큰 순서로 정렬
  const sortedWords = [...sentimentWords].sort((a, b) => b.value - a.value);

  // 나중에 뉴스 목록 띄우기로 변경
  const handleWordClick = (word: string) => {
    alert(`"${word}" 단어를 클릭했어!`);
  };

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
          <div className=" bg-[#F9F5EE] flex flex-col justify-center items-center">
            <WordCloud data={sentimentWords} onWordClick={handleWordClick} />
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
            <NewsCardList words={sortedWords} />
          </div>
        </div>
      </section>
    </div>
  );
}
