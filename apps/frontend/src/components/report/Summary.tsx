// src/components/report/Summary.tsx
import { useEffect, useState } from "react";
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
  companyName: string;
}

export default function Summary({ companyName }: SummaryProps) {
  const [data, setData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);

  /** 리포트 요약 API 호출 */
  useEffect(() => {
    const fetchSummary = async () => {
      try {
        if (!companyName) return;

        const BASE_URL = import.meta.env.VITE_API_BASE_URL;

        const res = await fetch(
          `${BASE_URL}/api/report/summary?company_name=${encodeURIComponent(
            companyName
          )}`
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
  }, [companyName]);

  if (loading) {
    return <div className="p-4 text-center text-gray-500">불러오는 중...</div>;
  }

  if (!data || !data.sentiment_ratio) {
    return (
      <div className="p-4 text-center text-gray-500">
        분석된 리포트 데이터가 없습니다.
      </div>
    );
  }

  const donutData = [
    { name: "긍정", value: data.sentiment_ratio?.positive ?? 0 },
    { name: "부정", value: data.sentiment_ratio?.negative ?? 0 },
    { name: "중립", value: data.sentiment_ratio?.neutral ?? 0 }
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
