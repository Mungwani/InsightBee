import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import type { NewsItem } from "../components/news/NewsList";
import ReportHeader from "../components/report/ReportHeader"; // ✅ 추가

interface LocationState {
    item?: NewsItem;
}

export default function NewsDetailPage() {
    const { id = "" } = useParams<{ id: string }>();
    const { state } = useLocation() as { state?: LocationState };
    const containerRef = useRef<HTMLDivElement>(null);

    const fallbackItem: NewsItem | undefined = useMemo(() => {
        const pool: NewsItem[] = [
            {
                id: "art_001",
                title: "[삼성전자] AI 투자 확대, HBM 생산능력 2배 증설",
                publisher: "연합뉴스",
                publishedAt: "2025-10-24T02:10:00Z",
                summary:
                    "삼성전자가 AI 반도체 수요 증가에 맞춰 HBM 생산능력 확대 계획 발표...",
                sentiment: "positive",
                url: "https://news.example.com/1",
                content: "본문...",
            },
        ];
        return pool.find((i) => i.id === id);
    }, [id]);

    const [item] = useState<NewsItem | undefined>(
        state?.item ?? fallbackItem
    );

    useEffect(() => {
        if (!item && id) {
            // TODO: fetch(`/api/news/${id}`).then(setItem)
        }
    }, [id, item]);

    useEffect(() => {
        containerRef.current?.scrollTo({ top: 0, behavior: "smooth" });
    }, [id]);

    return (
        <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
            {/* ✅ 통일된 노란 헤더 */}
            <ReportHeader title="기사 원문" />

            {/* ✅ 뉴스 본문 */}
            <main className="relative z-10 -mt-6 p-4 flex-1">
                <section
                    ref={containerRef}
                    className="bg-white rounded-2xl shadow p-5 max-w-4xl mx-auto"
                >
                    {item ? (
                        <>
                            <h1 className="text-2xl font-bold mb-2">{item.title}</h1>
                            <div className="text-sm text-gray-500 mb-4">
                                {item.publisher} •{" "}
                                {new Date(item.publishedAt).toLocaleString()}
                            </div>

                            {item.summary && (
                                <p className="text-gray-700 mb-4">{item.summary}</p>
                            )}

                            <article className="prose max-w-none text-gray-800">
                                {item.content ?? "원문 본문을 불러오는 중입니다..."}
                            </article>

                            <div className="mt-6">
                                {item.url && (
                                    <a
                                        href={item.url}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="px-4 py-2 rounded-lg font-semibold text-white transition"
                                        style={{ backgroundColor: "#4F200D" }}
                                    >
                                        원문 링크 열기
                                    </a>
                                )}
                            </div>
                        </>
                    ) : (
                        <div className="text-gray-500">해당 기사를 찾을 수 없습니다.</div>
                    )}
                </section>
            </main>
        </div>
    );
}
