import { useEffect, useState } from "react";
import DonutChart from "./DonutChart"; // ← DonutChartTest 말고 이걸 사용!

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

export default function Summary() {
  const [data, setData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);

  /** 리포트 요약 API 호출 */
  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const params = new URLSearchParams(location.search);
        const companyName = params.get("company_name");

        if (!companyName) return;

        const res = await fetch(
          `/api/report/summary?company_name=${encodeURIComponent(companyName)}`
        );
        const json = await res.json();

        setData(json);
      } catch (err) {
        console.error("요약 데이터 불러오기 오류:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return <div className="p-4 text-center text-gray-500">불러오는 중...</div>;
  }

  if (!data) {
    return (
      <div className="p-4 text-center text-red-500">
        요약 데이터를 찾을 수 없습니다.
      </div>
    );
  }

  /** 🔥 DonutChart에 맞게 데이터 변환 */
  const donutData = [
    { name: "긍정", value: data.sentiment_ratio.positive },
    { name: "부정", value: data.sentiment_ratio.negative },
    { name: "중립", value: data.sentiment_ratio.neutral },
  ] as const;

  return (
    <div className="mt-3 space-y-4 px-4 ">
      {/* 핵심 포인트 */}
      <section className="bg-white rounded-2xl shadow p-4">
        <h3 className="font-semibold mb-2 text-gray-700">
          {data.company_name} 핵심 포인트
        </h3>

        <div className="mb-3">
          <p className="text-green-600 font-bold mb-1">✅ 긍정 포인트</p>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
            {data.positive_points.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-red-600 font-bold mb-1">⚠️ 리스크 요인</p>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
            {data.risk_factors.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      </section>

      {/* 뉴스 긍부정 비율 */}
      <section className="bg-white rounded-2xl shadow p-4">
        <h3 className="font-semibold mb-3">뉴스 긍부정 비율</h3>

        <div className="flex justify-center">
          <DonutChart data={donutData} />
        </div>
      </section>
    </div>
  );
}
