import { useState, useRef, useEffect } from "react";
import Summary from "../components/report/Summary";
import KeywordNews from "../components/report/KeywordNews";
import ReportHeader from "../components/report/ReportHeader";
import { useLocation } from "react-router-dom";
import { fetchNewsByCompany } from "../services/report/getReport";
import { useParams } from "react-router-dom";

export default function ReportPage() {
  const { companyName } = useParams<{ companyName: string }>();
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

  // const location = useLocation();
  // const params = new URLSearchParams(location.search);
  // const companyName = params.get("company_name") || "기업명 없음";

  const scrollToTop = () => {
    containerRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };
  console.log(newsData);
  if (loading) return <div>뉴스를 불러오는 중...</div>;
  if (!newsData) return <div>뉴스 데이터가 없습니다</div>;
  return (
    <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
      {/* 헤더 */}
      <div className="relative z-0">
        <ReportHeader title="리포트" />
      </div>

      {/* 본문 */}
      <main className="relative z-10 -mt-6 p-4">
        {/* 기업 정보 카드 */}
        <section
          ref={containerRef}
          className="overflow-y-auto mx-0 bg-white rounded-2xl shadow p-4 flex flex-col gap-4 items-center justify-between"
        >
          <div className="flex gap-5 items-center w-full">
            <img
              src="/img/building.png"
              alt="company"
              className="ml-5 mt-2 w-13 h-auto"
            />

            {/* 본문-키워드별 뉴스 */}
            {tab === "keyword" && <KeywordNews newsData={newsData} />}
            <div className="flex flex-col">
              <div className="text-lg font-bold text-gray-500">
                {companyName}
              </div>

              <p className="text-sm text-gray-500">
                기업 기본 설명(추후 API 연동 가능)
              </p>
            </div>
          </div>

          <div className="border-b border-gray-300 w-[95%] h-2"></div>

          <div className="flex justify-around w-full">
            <div className="flex gap-2 items-center justify-center">
              <img
                className="w-[15px] h-[17px]"
                src="/img/report1.png"
                alt="기업"
              />
              <p className="text-[15px] text-gray-400 mt-1">업종 정보</p>
            </div>
            <div className="flex gap-2 items-center justify-center">
              <img
                className="w-[15px] h-[17px]"
                src="/img/report2.png"
                alt="기업"
              />
              <p className="text-[15px] text-gray-400 mt-1">
                최근 기사 분석 정보
              </p>
            </div>
          </div>
        </section>

        {/* 탭 메뉴 */}
        <div className="flex justify-center gap-3 mt-4">
          <button
            onClick={() => setTab("summary")}
            type="button"
            className={`w-[110px] h-[40px] rounded-full text-sm font-semibold ${
              tab === "summary"
                ? "bg-[#4F200D] text-white"
                : "bg-[#D7CCC8] text-[#4F200D]"
            }`}
          >
            핵심요약
          </button>

          <button
            onClick={() => setTab("keyword")}
            type="button"
            className={`w-[110px] h-[40px] rounded-full text-xs font-semibold ${
              tab === "keyword"
                ? "bg-[#4F200D] text-white"
                : "bg-[#D7CCC8] text-[#4F200D]"
            }`}
          >
            키워드별 뉴스
          </button>
        </div>

        {/* 탭 내용 */}
        <div className="overflow-y-auto mt-4 px-0 pb-16">
          {tab === "summary" && <Summary companyName={companyName} />}
          {tab === "keyword" && <KeywordNews companyName={companyName} />}
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
