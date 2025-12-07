import { AlertCircle, AlertTriangle, Check, Sparkles, TrendingUp, PieChart as ChartIcon } from "lucide-react";
import DonutChart from "./DonutChart";
import KeywordList from "./KeywordList";

interface SummaryData {
  company_name: string;
  // 뉴스 긍부정 비율 데이터 (fetchSummaryByCompany 결과)
  sentiment_ratio: {
    positive: number;
    negative: number;
    neutral: number;
  };
  // 핵심 포인트 데이터 (fetchPointsByCompany 결과)
  positive_points: string[];
  risk_factors: string[];

  // 키워드 목록
  keywords: { keyword: string }[];
}

interface SummaryProps {
  summaryData: SummaryData | null;
  loading: boolean;
}

export default function Summary({ summaryData }: SummaryProps) {

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

      {/* 1. 핵심 포인트 섹션 (주간 리포트 기반) */}
      <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-[#FFA000]" fill="#FFA000" />
          <h3 className="text-lg font-bold text-gray-800">
            핵심 포인트
          </h3>
          <span className="ml-25 text-xs text-gray-400">
            최근 1주일 기준
          </span>
        </div>

        <div className="flex flex-col gap-3">
          {/* 성장 기회 & 강점 */}
          <div className="bg-green-50 rounded-xl p-4 border border-green-100">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <p className="text-green-700 font-bold text-m">성장 기회 & 강점</p>
            </div>
            <ul className="space-y-2">
              {summaryData.positive_points.map((p, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <Check className="w-3.5 h-3.5 text-green-600 mt-[3px] flex-shrink-0" strokeWidth={3} />
                  <span className="leading-tight">{p}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 잠재적 리스크 */}
          <div className="bg-red-50 rounded-xl p-4 border border-red-100">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              <p className="text-red-700 font-bold text-m">잠재적 리스크</p>
            </div>
            <ul className="space-y-2">
              {summaryData.risk_factors.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <AlertCircle className="w-3.5 h-3.5 text-red-500 mt-[3px] flex-shrink-0" />
                  <span className="leading-tight">{r}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* 2. 뉴스 긍부정 비율 섹션 (Summary API 기반) */}
      <section className="bg-white rounded-2xl shadow p-4">
        <div className="flex items-center gap-2 mb-4">
          <ChartIcon className="w-5 h-5 text-blue-800" />
          <h3 className="text-lg font-bold text-gray-700">뉴스 긍부정 비율</h3>
        </div>

        <div className="flex justify-center w-full h-[300px]">
          <DonutChart data={donutData} />
        </div>
      </section>

      {/* 3. 키워드 목록 섹션 */}
      <KeywordList keywords={summaryData.keywords} />
    </div>
  );
}