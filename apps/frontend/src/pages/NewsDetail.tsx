/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import ReportHeader from "../components/report/ReportHeader";
import { Calendar, ExternalLink, Newspaper } from "lucide-react";

/** API 응답 타입 */
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
    const [error, setError] = useState("");

    /** API 호출 */
    useEffect(() => {
        const fetchDetail = async () => {
            try {
                setLoading(true);
                setError("");

                const res = await fetch(`/api/news/${id}`);
                if (!res.ok) throw new Error("뉴스 불러오기 실패");

                const json = await res.json();

                /** 👉 응답 형태 안전하게 처리 */
                const article =
                    json?.data ??
                    json?.result ??
                    json ??
                    null;

                if (!article || !article.article_id) {
                    throw new Error("유효한 기사 데이터를 찾을 수 없습니다.");
                }

                setItem(article);
            } catch (e: any) {
                console.error(e);
                setError(e.message ?? "오류가 발생했습니다.");
            } finally {
                setLoading(false);
            }
        };

        fetchDetail();
    }, [id]);

    /** 스크롤 맨 위로 이동 */
    useEffect(() => {
        containerRef.current?.scrollTo({ top: 0, behavior: "smooth" });
    }, [item]);

    /** -------------------------
     *      로딩 화면 (귀여운 꿀벌 로딩)
     -------------------------- */
    if (loading) {
        return (
            <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
                <ReportHeader title="기사 원문" />

                <main className="flex flex-col items-center justify-center flex-1 text-gray-500 relative overflow-hidden">

                    {/* 🐝 돌아다니는 꿀벌 */}
                    <img
                        src="/img/newsBee.svg"
                        alt="bee"
                        className="w-24 h-24"
                    />

                    <p className="mt-6 text-[#4F200D]/70 font-medium animate-pulse">
                        불러오는 중...
                    </p>
                </main>
            </div>
        );
    }


    /** -------------------------
     *      에러 화면
     -------------------------- */
    if (error) {
        return (
            <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
                <ReportHeader title="기사 원문" />
                <main className="flex flex-col items-center justify-center flex-1 text-gray-500">
                    <Newspaper className="w-14 h-14 opacity-30 mb-4" />
                    <p className="font-medium">{error}</p>
                </main>
            </div>
        );
    }

    /** -------------------------
     *      데이터 없음
     -------------------------- */
    if (!item) {
        return (
            <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
                <ReportHeader title="기사 원문" />
                <main className="flex flex-col items-center justify-center flex-1 text-gray-400">
                    <Newspaper className="w-14 h-14 opacity-30 mb-4" />
                    <p className="font-medium">해당 기사를 찾을 수 없습니다.</p>
                </main>
            </div>
        );
    }

    /** -------------------------
     *      정상 화면
     -------------------------- */
    return (
        <div className="min-h-screen bg-[#F9F5EE] flex flex-col">
            <ReportHeader title="기사 원문" />

            <main
                ref={containerRef}
                className="flex-1 px-4 pb-10 sm:px-6 md:px-8 -mt-4 relative z-10 pt-8"
            >
                <section className="max-w-3xl mx-auto bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-stone-100 overflow-hidden">

                    {/* 1) 헤더 */}
                    <div className="p-6 border-b border-stone-100 bg-white">
                        <span className="inline-block px-3 py-1 mb-4 text-xs font-bold tracking-wider text-[#4F200D] bg-[#4F200D]/10 rounded-full">
                            NEWS ARTICLE
                        </span>

                        <h1 className="text-2xl font-bold text-gray-900 mb-6 leading-snug">
                            {item.title}
                        </h1>

                        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 font-medium">
                            <div className="flex items-center gap-1.5">
                                <Newspaper className="w-4 h-4 text-[#4F200D]/70" />
                                <span>{item.source}</span>
                            </div>

                            <div className="flex items-center gap-1.5">
                                <Calendar className="w-4 h-4 text-[#4F200D]/70" />
                                <span>{new Date(item.published_at).toLocaleString()}</span>
                            </div>
                        </div>
                    </div>

                    {/* 2) Key Summary */}
                    <div className="p-6 bg-white">
                        {item.key_summary && (
                            <div className="relative">
                                <div className="relative bg-[#F9F7F3] rounded-2xl p-6 md:p-8 border border-[#EBE5D5]">
                                    <h3 className="text-[#4F200D] font-bold mb-4 text-sm tracking-wide uppercase flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 rounded-full bg-[#4F200D]" />
                                        Key Summary
                                    </h3>
                                    <p className="text-gray-800 leading-relaxed whitespace-pre-line text-base md:text-lg font-medium">
                                        {item.key_summary}
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* 3) 원문 링크 */}
                        <div className="mt-10 flex justify-center">
                            <a
                                href={item.original_link}
                                target="_blank"
                                rel="noreferrer"
                                className="group inline-flex items-center justify-center gap-2 px-8 py-4 w-full sm:w-auto
                                bg-[#4F200D] text-white font-bold rounded-xl shadow-md 
                                transition-all duration-300 hover:bg-[#3E190A] hover:shadow-lg hover:-translate-y-0.5"
                            >
                                원문 전체 읽기
                                <ExternalLink className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                            </a>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}
