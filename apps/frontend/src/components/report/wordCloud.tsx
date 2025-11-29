// import WordCloudLib from "react-wordcloud";
// import type { WordData } from "../../../public/data/newsData";

// interface WordCloudProps {
//   data: WordData[];
//   onWordClick?: (word: string) => void;
// }

// export default function WordCloud({ data, onWordClick }: WordCloudProps) {
//   const options = {
//     rotations: 2,
//     rotationAngles: [0, 90] as [number, number],
//     fontFamily: "Pretendard, sans-serif",
//     fontSizes: [20, 60] as [number, number],
//     padding: 5,
//     deterministic: true,
//   };

//   const callbacks = {
//     getWordColor: (word: any) =>
//       word.sentiment === "positive" ? "#00C851" : "#ff4444",
//     onWordClick: (word: any) => {
//       if (onWordClick) onWordClick(word.text);
//     },
//   };

//   return (
//     <div className="flex flex-col justify-center items-center w-full h-[400px] bg-white rounded-2xl shadow-sm">
//       <WordCloudLib words={data} options={options} callbacks={callbacks} />
//     </div>
//   );
// }
