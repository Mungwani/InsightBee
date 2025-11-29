import DonutChart from "./DonutChart";

interface SummaryData {
  company_name: string;
  sentiment_ratio: {
    positive: number;
    negative: number;
    neutral: number;
  };
  positive_points: string[];
  risk_factors: string[];
}

interface SummaryProps {
  summaryData: SummaryData | null;
  loading: boolean;
}

export default function Summary({ summaryData, loading }: SummaryProps) {
  if (loading) {
    return <div className="p-4 text-center text-gray-500">불러오는 중...</div>;
  }

  if (!summaryData || !summaryData.sentiment_ratio) {
    return (
      <div className="p-4 text-center text-gray-500">
        분석된 리포트 데이터가 없습니다.
      </div>
    );
  }

  const donutData = [
    { name: "긍정", value: summaryData.sentiment_ratio.positive ?? 0 },
    { name: "부정", value: summaryData.sentiment_ratio.negative ?? 0 },
    { name: "중립", value: summaryData.sentiment_ratio.neutral ?? 0 },
  ] as const;

  return (
    <div className="mt-3 space-y-4 px-4">
      <section className="bg-white rounded-2xl shadow p-4">
        <h3 className="font-semibold mb-2 text-gray-700">
          {summaryData.company_name} 핵심 포인트
        </h3>

        <div className="mb-3">
          <p className="text-green-600 font-bold mb-1">긍정 포인트</p>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
            {summaryData.positive_points.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-red-600 font-bold mb-1">리스크 요인</p>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
            {summaryData.risk_factors.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="bg-white rounded-2xl shadow p-4">
        <h3 className="font-semibold mb-3">뉴스 긍부정 비율</h3>

        <div className="flex justify-center">
          <DonutChart data={donutData} />
        </div>
      </section>
    </div>
  );
}
