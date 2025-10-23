import { useState, useRef } from "react";
import Summary from "../components/report/Summary";
import KeywordNews from "../components/report/KeywordNews";
import Tip from "../components/report/Tip";
import ReportHeader from "../components/report/ReportHeader";

export default function ReportPage() {
  const [tab, setTab] = useState("summary");
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToTop = () => {
    containerRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
      {/* 헤더는 뒤(z-0) */}
      <div className="relative z-0">
        <ReportHeader title="리포트" />
      </div>

      {/* 본문은 앞(z-10) + 위로 살짝 겹치기 */}
      <main className="relative z-10 -mt-6 p-4">
        {/* 기업 정보 카드 */}
        <section
          ref={containerRef}
          className="overflow-y-auto mx-0 bg-white rounded-2xl shadow p-4 flex flex-col gap-4 items-center justify-between"
        >
          <div className="flex gap-5 items-center w-full">
            <img src="/img/exLogo.png" alt="samsung" className="w-20 h-auto" />
            <div className="flex flex-col">
              <div className="text-lg font-bold text-gray-500">삼성전자</div>
              <p className="text-sm text-gray-500">
                반도체, IT · 가전의 세계적 선도 기업
              </p>
            </div>
          </div>

          <div className="border-b border-gray-300 w-[95%] h-2"></div>

          <div className="flex justify-around w-full">
            <div className="flex gap-2 items-center justify-center">
              <img className="w-[15px] h-[17px]" src="/img/report1.png" alt="기업" />
              <p className="text-[15px] text-gray-400 mt-1">반도체/IT</p>
            </div>
            <div className="flex gap-2 items-center justify-center">
              <img className="w-[15px] h-[17px]" src="/img/report2.png" alt="기업" />
              <p className="text-[15px] text-gray-400 mt-1">
                최근 7일간 총 24개의 기사 분석
              </p>
            </div>
          </div>
        </section>

        {/* 탭 메뉴 */}
        <div className="flex justify-center gap-3 mt-4">
          <button
            onClick={() => setTab("summary")}
            type="button"
            className={`w-[110px] h-[40px] rounded-full text-sm font-semibold ${tab === "summary" ? "bg-[#4F200D] text-white" : "bg-[#D7CCC8] text-[#4F200D]"
              }`}
          >
            핵심요약
          </button>
          <button
            onClick={() => setTab("keyword")}
            type="button"
            className={`w-[110px] h-[40px] rounded-full text-xs font-semibold ${tab === "keyword" ? "bg-[#4F200D] text-white" : "bg-[#D7CCC8] text-[#4F200D]"
              }`}
          >
            키워드별 뉴스
          </button>
          <button
            onClick={() => setTab("tip")}
            type="button"
            className={`w-[110px] h-[40px] rounded-full text-sm font-semibold ${tab === "tip" ? "bg-[#4F200D] text-white" : "bg-[#D7CCC8] text-[#4F200D]"
              }`}
          >
            면접 TIP
          </button>
        </div>

        {/* 탭 내용 */}
        <div className="overflow-y-auto mt-4 px-0 pb-16">
          {tab === "summary" && <Summary />}
          {tab === "keyword" && <KeywordNews />}
          {tab === "tip" && <Tip />}
        </div>
      </main>

      {/* 맨 위로 버튼 */}
      <button
        onClick={scrollToTop}
        className="fixed bottom-6 right-6 bg-[#5B2C02] text-white p-3 rounded-full shadow-lg"
      >
        ↑
      </button>
    </div>
  );
}
