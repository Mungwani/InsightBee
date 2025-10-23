// src/pages/ReportKeyword.tsx
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import NewsList from "../components/news/NewsList";
import type { NewsItem } from "../components/news/NewsList";
import ReportHeader from "../components/report/ReportHeader";

export default function ReportKeywordPage() {
    const navigate = useNavigate();

    const items: NewsItem[] = useMemo(
        () => [
            {
                id: "art_001",
                title: "[삼성전자] AI 투자 확대, HBM 생산능력 2배 증설",
                publisher: "연합뉴스",
                publishedAt: "2025-10-24T02:10:00Z",
                url: "https://news.example.com/1",
                summary: "삼성전자가 AI 반도체 수요 증가에 맞춰 HBM 생산능력 확대 계획을 발표...",
                sentiment: "positive",
                content:
                    "삼성전자는 차세대 AI 반도체 수요를 고려해 HBM 생산능력을 2배 수준으로 확대한다고 밝혔다. 또한 신규 라인에 대한 투자와 협력사와의 공급망 강화를 병행할 계획이다...",
            },
            {
                id: "art_002",
                title: "글로벌 경기 둔화 우려 속 IT 업종 혼조",
                publisher: "매일경제",
                publishedAt: "2025-10-23T12:30:00Z",
                url: "https://news.example.com/2",
                summary: "글로벌 금리 고점론이 해소되지 않으며 IT 업종은 종목별로 차별화된 흐름을...",
                sentiment: "neutral",
                content:
                    "글로벌 경기 둔화 우려가 해소되지 않은 가운데 IT 업종은 기업별로 실적과 모멘텀에 따른 차별화가 커지고 있다. 전문가들은 AI 관련 설비투자 지속 여부를 핵심 변수로 꼽았다...",
            },
            {
                id: "art_003",
                title: "반도체 업황 둔화 우려 재부각…재고조정 장기화 가능성",
                publisher: "한국경제",
                publishedAt: "2025-10-22T08:05:00Z",
                url: "https://news.example.com/3",
                summary: "일부 시장에서는 재고조정 국면이 예상보다 길어질 수 있다는 분석이 제기되며...",
                sentiment: "negative",
                content:
                    "일부 애널리스트는 PC와 모바일 수요 회복 속도가 더디고 재고조정이 장기화될 가능성을 언급했다. 다만 AI 서버 수요는 견조해 업체별 영향은 상이할 전망이다...",
            },
        ],
        []
    );


    const goDetail = (id: string) => {
        const item = items.find((i) => i.id === id);
        navigate(`/report/keyword/news-detail/${id}`, { state: { item } });
    };

    return (
        <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
            {/* 헤더는 뒤(z-0) */}
            <div className="relative z-0">
                <ReportHeader title="키워드별 뉴스" />
            </div>

            {/* 본문은 앞(z-10) + 위로 살짝 겹치기(-mt-4 ~ -mt-8 조정) */}
            <main className="relative z-10 -mt-6 p-4">
                <section className="bg-white rounded-2xl shadow overflow-hidden">
                    <div className="px-4 py-3 border-b flex items-center justify-between">
                        <div>
                            <div className="text-sm text-gray-600">관련 뉴스</div>
                            <div className="text-base font-semibold text-[#4F200D]">{items.length}건</div>
                        </div>
                    </div>

                    <div className="max-h-[75vh] overflow-y-auto">
                        <NewsList items={items} onRead={goDetail} />
                    </div>
                </section>
            </main>
        </div>

    );
}
