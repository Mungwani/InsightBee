import { useState } from "react";
import { useEffect } from "react";
import Summary from "../components/report/Summary";
import KeywordNews from "../components/report/KeywordNews";
import Tip from "../components/report/Tip";
import { useRef } from "react";
import { fetchNewsByCompany } from "../services/report/getReport";
import { useParams } from "react-router-dom";

export default function ReportPage() {
  const { companyName } = useParams();
  const [newsData, setNewsData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!companyName) return;
    fetchNewsByCompany(companyName)
      .then((data) => {
        setNewsData(data);
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const [tab, setTab] = useState("summary");
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToTop = () => {
    if (containerRef.current) {
      containerRef.current.scrollTo({ top: 0, behavior: "smooth" });
    }
  };
  console.log(newsData);
  if (loading) return <div>뉴스를 불러오는 중...</div>;
  if (!newsData) return <div>뉴스 데이터가 없습니다</div>;
  return (
    <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
      {/* 상단 헤더 */}
      <header className="flex items-center gap-7 p-4 bg-customYellow">
        <button className="mr-2 !font-bold !text-[20px] !bg-customYellow text-customBrown">
          ←
        </button>
        <div className="w-[45%] flex justify-center items-center">
          <div className="text-xl font-bold text-customBrown">리포트</div>
        </div>
      </header>

      {/* 기업 정보 카드 */}
      <section
        ref={containerRef}
        className="overflow-y-auto mx-4 mt-3 bg-white rounded-2xl shadow p-4 flex flex-col gap-4 items-center justify-between"
      >
        <div className="flex gap-5 items-center">
          <img src="/img/exLogo.png" alt="samsung" className="w-20 h-auto" />
          <div className="flex flex-col">
            <div className="text-lg font-bold text-gray-500">삼성전자</div>
            <p className="text-sm text-gray-500">
              반도체, IT · 가전의 세계적 선도 기업
            </p>
          </div>
        </div>
        <div className="border-b-1 border-gray-300 w-[95%] h-2"></div>
        <div className="flex justify-around w-full">
          <div className="flex gap-2 items-center justify-center">
            <img
              className="w-[15px] h-[17px]  "
              src="/img/report1.png"
              alt="기업"
            ></img>
            <p className="text-[15px] text-gray-400 mt-1">반도체/IT</p>
          </div>
          <div className="flex gap-2 items-center justify-center">
            <img
              className="w-[15px] h-[17px]  "
              src="/img/report2.png"
              alt="기업"
            ></img>
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
          className="w-[110px] h-[40px] !bg-customBrown rounded-full !text-sm font-semibold"
        >
          핵심요약
        </button>
        <button
          onClick={() => setTab("keyword")}
          type="button"
          className="w-[110px] h-[40px] !bg-customBrown rounded-full !text-xs"
        >
          키워드별 뉴스
        </button>
        <button
          onClick={() => setTab("tip")}
          type="button"
          className="w-[110px] h-[40px] !bg-customBrown rounded-full !text-sm"
        >
          면접 TIP
        </button>
      </div>

      <div className="flex-1 overflow-y-auto mt-4  px-4 pb-16">
        {/* 본문-핵심요약 */}
        {tab === "summary" && <Summary />}

        {/* 본문-키워드별 뉴스 */}
        {tab === "keyword" && <KeywordNews newsData={newsData} />}

        {/* 본문-면접 tip */}
        {tab === "tip" && <Tip />}
      </div>

      {/* 맨 위로 버튼 */}
      <button
        onClick={scrollToTop}
        className="fixed bottom-6 right-6 !bg-[#5B2C02] text-white p-3 rounded-full shadow-lg"
      >
        ↑
      </button>
    </div>
  );
}
