// src/pages/Report.tsx
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useRef } from "react";
import { useParams, useLocation } from "react-router-dom";
import Summary from "../components/report/mainSummary/Summary";
import KeywordNews from "../components/report/keyword/KeywordNews";
import ReportHeader from "../components/report/ReportHeader";
import { Building2, Newspaper, ArrowUp } from "lucide-react";
import News from "../components/report/newsList/News";

/**
 * 기업 분석 리포트 메인 페이지 컴포넌트
 * URL 파라미터와 라우터 state를 통해 데이터를 받아와 핵심 요약, 전체 뉴스, 키워드별 뉴스를 탭으로 보여줍니다.
 */
export default function ReportPage() {
  // 1. 상태 및 데이터 초기화

  // URL에서 기업 이름을 추출합니다. (예: /report/삼성전자)
  const { companyName } = useParams() as { companyName: string };

  // 라우터 state에서 서버로부터 전달받은 핵심 데이터 (summary, news, keywords)를 추출합니다.
  const { state } = useLocation() as {
    state?: { summary: any; news: any; keywords: any };
  };

  // 현재 활성화된 탭 상태를 관리합니다: "summary", "news", "keyword" 중 하나
  const [tab, setTab] = useState("summary");

  // 스크롤을 맨 위로 이동시키기 위해 메인 컨텐츠 영역의 DOM 요소에 접근하기 위한 ref
  const containerRef = useRef<HTMLDivElement>(null);

  // 2. 데이터 유효성 검사 (Empty State)

  // state나 필수 데이터(summary, news)가 없는 경우 (예: 새로고침 또는 비정상적 접근 시) 오류 화면을 렌더링합니다.
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

  // 데이터 구조 분해 및 가공
  const { summary, news, keywords } = state;
  // Summary 컴포넌트에 전달하기 위해 키워드 데이터를 summary 객체에 통합합니다.
  const summaryData = {
    ...summary,
    keywords: keywords?.keywords ?? []
  };

  // 3. 이벤트 핸들러

  // 메인 컨텐츠 영역을 맨 위로 스크롤하는 함수
  const scrollToTop = () => {
    // ref를 사용하여 DOM 요소에 접근 후, 부드러운 스크롤 효과를 적용
    containerRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };

  // 4. 컴포넌트 렌더링
  return (
    <div className="min-h-screen bg-[#F9F5EE] flex flex-col overflow-x-hidden">
      {/* 리포트 페이지 상단 헤더 */}
      <div className="relative z-0">
        <ReportHeader title="리포트" />
      </div>

      <main className="relative z-10 -mt-6 p-4">
        {/* 기업 정보 표시 섹션 */}
        <section
          ref={containerRef}
          className="bg-white rounded-2xl shadow-sm border border-[#EBE5DD] p-5 w-full flex flex-col"
        >
          {/* 기업 이름 및 아이콘 */}
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

          {/* 분석 기간 정보 */}
          <div className="w-full flex gap-2 items-center justify-end">
            <Newspaper className="w-4 h-4 text-gray-400" />
            <p className="text-[15px] text-gray-400">
              최근 3개월 {summaryData.total_article_count}건 기반
            </p>
          </div>
        </section>

        {/* 탭 네비게이션 버튼 */}
        <div className="flex justify-center gap-1.5 mt-8">
          {/* 핵심요약 탭 */}
          <button
            onClick={() => setTab("summary")}
            className={`w-[120px] h-[40px] rounded-full text-sm font-semibold transition-colors duration-200 ${tab === "summary"
              ? "bg-[#4F200D] text-white"
              : "bg-[#D7CCC8] text-[#4F200D]"
              }`}
          >
            핵심요약
          </button>

          {/* 전체 뉴스 탭 */}
          <button
            onClick={() => setTab("news")}
            className={`w-[120px] h-[40px] rounded-full text-sm font-semibold transition-colors duration-200 ${tab === "news"
              ? "bg-[#4F200D] text-white"
              : "bg-[#D7CCC8] text-[#4F200D]"
              }`}
          >
            전체 뉴스
          </button>

          {/* 키워드별 뉴스 탭 */}
          <button
            onClick={() => setTab("keyword")}
            className={`w-[120px] h-[40px] rounded-full text-sm font-semibold transition-colors duration-200 ${tab === "keyword"
              ? "bg-[#4F200D] text-white"
              : "bg-[#D7CCC8] text-[#4F200D]"
              }`}
          >
            키워드별 뉴스
          </button>
        </div>

        {/* 탭 컨텐츠 영역 */}
        <div className="overflow-y-auto mt-4 px-0 pb-16">
          {/* 핵심요약 탭 컨텐츠 */}
          {tab === "summary" && (
            <Summary summaryData={summaryData} loading={false} />
          )}

          {/* 전체 뉴스 탭 컨텐츠 (NewsData prop 이름 사용) */}
          {tab === "news" && <News newsData={news} />}

          {/* 키워드별 뉴스 탭 컨텐츠 */}
          {tab === "keyword" && (
            <KeywordNews newsData={news} companyName={companyName!} />
          )}
        </div>
      </main>

      {/* 스크롤 맨 위로 이동 버튼 */}
      <button
        onClick={scrollToTop}
        className="fixed bottom-6 right-6 
        bg-[#4F200D] text-white p-3 rounded-full shadow-xl z-50
        flex items-center justify-center"
      >
        <ArrowUp className="w-5 h-5" strokeWidth={3} />
      </button>
    </div>
  );
}