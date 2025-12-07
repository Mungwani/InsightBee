/* eslint-disable @typescript-eslint/no-explicit-any */
// src/pages/Report.tsx
import { useState, useRef } from "react";
import { useParams, useLocation } from "react-router-dom";
import Summary from "../components/report/mainSummary/Summary";
import KeywordNews from "../components/report/keyword/KeywordNews";
import ReportHeader from "../components/report/ReportHeader";
import { Building2, Newspaper, ArrowUp } from "lucide-react";

export default function ReportPage() {
  const { companyName } = useParams() as { companyName: string };
  const { state } = useLocation() as {
    state?: { summary: any; news: any; keywords: any };
  };

  const [tab, setTab] = useState("summary");
  const containerRef = useRef<HTMLDivElement>(null);

  if (!state || !state.summary || !state.news) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#F9F5EE] text-gray-500">
        <div className="p-6 text-center">
          <p className="text-lg font-bold mb-2">데이터가 없습니다.</p>
          <p className="text-sm">새로고침을 하셨거나 올바르지 않은 접근입니다.<br />메인 화면에서 다시 검색해주세요.</p>
        </div>
      </div>
    );
  }

  const { summary, news, keywords } = state;
  const summaryData = {
    ...summary,
    keywords: keywords?.keywords ?? []
  };

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
          className="bg-white rounded-2xl shadow-sm border border-[#EBE5DD] p-5 w-full flex flex-col"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-[#FFF8E1] flex items-center justify-center flex-shrink-0">
              <Building2 className="w-6 h-6 text-[#FFA000]" strokeWidth={2} />
            </div>

            <div className="flex flex-col justify-center">
              <span className="text-xs font-semibold text-gray-400 mb-0.5">분석 기업</span>
              <div className="text-xl font-extrabold text-[#4F200D] leading-none">
                {companyName}
              </div>
            </div>
          </div>

          <div className="h-px bg-gray-100 w-full my-4"></div>

          <div className="w-full flex gap-2 items-center justify-end">
            <Newspaper className="w-4 h-4 text-gray-400" />
            <p className="text-[15px] text-gray-400">
              최근 3개월 {summaryData.total_article_count}건 기반
            </p>
          </div>
        </section>

        <div className="flex justify-center gap-5 mt-8">
          <button
            onClick={() => setTab("summary")}
            className={`w-[140px] h-[40px] rounded-full text-sm font-semibold transition-colors duration-200 ${
              tab === "summary"
                ? "bg-[#4F200D] text-white"
                : "bg-[#D7CCC8] text-[#4F200D]"
            }`}
          >
            핵심요약
          </button>

          <button
            onClick={() => setTab("news")}
            className={`w-[140px] h-[40px] rounded-full text-sm font-semibold transition-colors duration-200 ${
              tab === "news"
                ? "bg-[#4F200D] text-white"
                : "bg-[#D7CCC8] text-[#4F200D]"
            }`}
          >
            전체 뉴스
          </button>

          <button
            onClick={() => setTab("keyword")}
            className={`w-[140px] h-[40px] rounded-full text-sm font-semibold transition-colors duration-200 ${
              tab === "keyword"
                ? "bg-[#4F200D] text-white"
                : "bg-[#D7CCC8] text-[#4F200D]"
            }`}
          >
            키워드별 뉴스
          </button>
        </div>

        <div className="overflow-y-auto mt-4 px-0 pb-16">
          {tab === "summary" && (
            <Summary summaryData={summaryData} loading={false} />
          )}

          {tab === "news" && <News newsData={newsData} />}

          {tab === "keyword" && (
            <KeywordNews newsData={news} companyName={companyName!} />
          )}
        </div>
      </main>

      <button
        onClick={scrollToTop}
        className="fixed bottom-6 right-6 
               bg-[#4F200D] text-white p-3 rounded-full shadow-xl 
               transition-all duration-300 hover:bg-[#3E1E04] active:scale-95
               flex items-center justify-center"
      >
        <ArrowUp className="w-5 h-5" strokeWidth={3} />
      </button>
    </div>
  );
}