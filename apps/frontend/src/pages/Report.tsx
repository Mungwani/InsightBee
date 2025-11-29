// src/pages/Report.tsx
import { useState, useRef } from "react";
import { useParams, useLocation } from "react-router-dom";
import Summary from "../components/report/mainSummary/Summary";
import KeywordNews from "../components/report/keyword/KeywordNews";
import ReportHeader from "../components/report/ReportHeader";

export default function ReportPage() {
  const { companyName } = useParams() as { companyName: string };
  const { state } = useLocation() as {
    state?: { summary: any; news: any };
  };

  const summaryData = state?.summary;
  const newsData = state?.news;

  const [tab, setTab] = useState("summary");
  const containerRef = useRef<HTMLDivElement>(null);

  /** ❗ 새로고침하면 state가 사라지므로 fallback */
  if (!summaryData || !newsData) {
    return <div className="p-6">데이터가 없습니다. (새로고침 금지)</div>;
  }

  const scrollToTop = () => {
    containerRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-[#F9F5EE] flex flex-col overflow-x-hidden">
      <div className="relative z-0">
        <ReportHeader title="리포트" />
      </div>

      <main className="relative z-10 -mt-6 p-4">
        <section
          ref={containerRef}
          className="overflow-y-auto bg-white rounded-2xl shadow p-4 flex flex-col gap-4 overflow-x-hidden"
        >
          <div className="flex gap-5 items-center w-full">
            <img src="/img/building.png" className="ml-5 mt-2 w-13" />
            <div className="flex flex-col">
              <div className="text-lg font-bold text-gray-500">{companyName}</div>
              <p className="text-sm text-gray-500">기업 기본 설명(추후 API 연동 가능)</p>
            </div>
          </div>

          <div className="border-b border-gray-300 w-[95%] h-2"></div>

          <div className="flex justify-around w-full">
            <div className="flex gap-2 items-center justify-center">
              <img className="w-[15px] h-[17px]" src="/img/report1.png" alt="업종" />
              <p className="text-[15px] text-gray-400 mt-1">업종 정보</p>
            </div>
            <div className="flex gap-2 items-center justify-center">
              <img className="w-[15px] h-[17px]" src="/img/report2.png" alt="기사" />
              <p className="text-[15px] text-gray-400 mt-1">최근 기사 분석 정보</p>
            </div>
          </div>
        </section>

        <div className="flex justify-center gap-3 mt-4">
          <button
            onClick={() => setTab("summary")}
            className={`w-[110px] h-[40px] rounded-full text-sm font-semibold ${tab === "summary" ? "bg-[#4F200D] text-white" : "bg-[#D7CCC8] text-[#4F200D]"
              }`}
          >
            핵심요약
          </button>

          <button
            onClick={() => setTab("keyword")}
            className={`w-[110px] h-[40px] rounded-full text-xs font-semibold ${tab === "keyword" ? "bg-[#4F200D] text-white" : "bg-[#D7CCC8] text-[#4F200D]"
              }`}
          >
            키워드별 뉴스
          </button>
        </div>

        <div className="overflow-y-auto mt-4 px-0 pb-16">
          {tab === "summary" && (
            <Summary summaryData={summaryData} loading={false} />
          )}

          {tab === "keyword" && (
            <KeywordNews newsData={newsData} companyName={companyName!} />
          )}
        </div>
      </main>

      <button
        onClick={scrollToTop}
        className="fixed bottom-6 right-6 bg-[#5B2C02] text-white p-3 rounded-full shadow-lg"
      >
        ↑
      </button>
    </div>
  );
}
