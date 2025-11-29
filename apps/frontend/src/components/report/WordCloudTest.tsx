import WordCloud from "./wordCloud";
import type { WordData } from "./wordCloud";

export default function WordCloudTest() {
  const sentimentWords: WordData[] = [
    // ✅ 긍정
    { text: "주식", value: 50, sentiment: "positive" },
    { text: "오른다", value: 40, sentiment: "positive" },
    { text: "화이팅", value: 35, sentiment: "positive" },
    { text: "가즈아", value: 25, sentiment: "positive" },
    { text: "화성", value: 20, sentiment: "positive" },
    // ✅ 부정
    { text: "으아ㅏ악", value: 45, sentiment: "negative" },
    { text: "그만", value: 40, sentiment: "negative" },
    { text: "떨어져", value: 35, sentiment: "negative" },
    { text: "제발", value: 25, sentiment: "negative" },
    { text: "물타기", value: 20, sentiment: "negative" },
  ];

  const handleWordClick = (word: string) => {
    alert(`"${word}" 단어를 클릭했어!`);
  };

  return (
    <div className=" bg-[#F9F5EE] flex flex-col justify-center items-center">
      <WordCloud data={sentimentWords} onWordClick={handleWordClick} />
    </div>
  );
}
