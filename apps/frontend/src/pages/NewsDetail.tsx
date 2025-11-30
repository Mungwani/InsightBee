import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import ReportHeader from "../components/report/ReportHeader";

/** ✅ API 응답 타입 정의 */
interface NewsDetail {
    article_id: number;
    title: string;
    source: string;
    published_at: string;
    key_summary: string;
    original_link: string;
}

export default function NewsDetailPage() {
    const { id = "" } = useParams<{ id: string }>();
    const containerRef = useRef<HTMLDivElement>(null);

    const [item, setItem] = useState<NewsDetail | null>(null);
    const [loading, setLoading] = useState(true);

    /** ✅ API 호출: /api/news/{article_id} */
    useEffect(() => {
        const fetchDetail = async () => {
            try {
                const res = await fetch(`/api/news/${id}`);
                if (!res.ok) throw new Error("뉴스 불러오기 실패");
                const json: NewsDetail = await res.json();
                setItem(json);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };

        fetchDetail();
    }, [id]);

    /** 스크롤 맨 위로 이동 */
    useEffect(() => {
        containerRef.current?.scrollTo({ top: 0, behavior: "smooth" });
    }, [id]);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
                <ReportHeader title="기사 원문" />
                <main className="p-4 text-center text-gray-500">불러오는 중...</main>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
            {/* 상단 헤더 */}
            <ReportHeader title="기사 원문" />

            {/* 본문 */}
            <main className="relative z-10 -mt-6 p-4 flex-1">
                <section
                    ref={containerRef}
                    className="bg-white rounded-2xl shadow p-5 max-w-4xl mx-auto"
                >
                    {item ? (
                        <>
                            {/* 제목 */}
                            <h1 className="text-2xl font-bold mb-2">{item.title}</h1>

                            {/* 언론사 + 발행일 */}
                            <div className="text-sm text-gray-500 mb-4">
                                {item.source} •{" "}
                                {new Date(item.published_at).toLocaleString()}
                            </div>

                            {/* 핵심 요약 */}
                            {item.key_summary && (
                                <p className="text-gray-700 mb-4 whitespace-pre-line">
                                    {item.key_summary}
                                </p>
                            )}

                            {/* 원문 이동 버튼 */}
                            <div className="mt-6">
                                {item.original_link && (
                                    <a
                                        href={item.original_link}
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
                        <div className="text-gray-500">
                            해당 기사를 찾을 수 없습니다.
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}
