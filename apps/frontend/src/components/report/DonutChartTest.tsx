import DonutChart from "./DonutChart";

export default function DonutChartTest() {
  const sentimentData = [
    { name: "긍정", value: 54 },
    { name: "부정", value: 31 },
    { name: "중립", value: 15 },
  ] as const;

  return (
    <div className="flex justify-center items-center bg-white">
      <DonutChart data={sentimentData} />
    </div>
  );
}
