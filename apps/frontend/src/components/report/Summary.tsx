import DonutChartTest from "./DonutChartTest";

export default function Summary() {
  return (
    <div className="mt-3 space-y-4 px-4 ">
      {/* 핵심 포인트 */}
      <section className="bg-white rounded-2xl shadow p-4">
        <h3 className="font-semibold mb-2 text-gray-700">핵심 포인트</h3>

        <div className="mb-3">
          <p className="text-green-600 font-bold mb-1">✅ 긍정 포인트</p>
          <ul className="list-disc list-inside text-sm text-gray-700">
            <li>3분기 실적 예상 상회로 주식올랄라라라아아아</li>
            <li>신규 AI 사업 진출을 통한 가즈아앙아아</li>
            <li>반도체 수익성 회복 신호 반등가자으아앙아ㅏ</li>
          </ul>
        </div>

        <div>
          <p className="text-red-600 font-bold mb-1">⚠️ 리스크 요인</p>
          <ul className="list-disc list-inside text-sm text-gray-700">
            <li>글로벌 경기 둔화로 인한 폭락장 오나아ㅏㅏ</li>
            <li>원화 환율 변동 그만 올라라라ㅏ아</li>
          </ul>
        </div>
      </section>

      {/* 뉴스 긍부정 비율 */}
      <section className="bg-white rounded-2xl shadow p-4">
        <h3 className="font-semibold mb-3">뉴스 긍부정 비율</h3>
        <div className="flex justify-center">
          {/* 여기엔 실제 도넛 차트 들어감 */}
          <DonutChartTest />
        </div>
      </section>

      {/* 핵심 키워드 */}
      <section className="bg-white rounded-2xl shadow p-4">
        <h3 className="font-semibold mb-2 text-black">핵심 키워드</h3>
        <div className="flex flex-wrap gap-2 text-black">
          <span className="px-3 py-1 bg-yellow-100 rounded-full text-sm">
            #AI
          </span>
          <span className="px-3 py-1 bg-yellow-100 rounded-full text-sm">
            #반도체
          </span>
          <span className="px-3 py-1 bg-yellow-100 rounded-full text-sm">
            #전망
          </span>
        </div>
      </section>
    </div>
  );
}
