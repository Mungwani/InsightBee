import { Hash } from "lucide-react";

interface KeywordListProps {
    keywords: { keyword: string }[];
}

export default function KeywordList({ keywords }: KeywordListProps) {
    const hasKeywords = keywords && keywords.length > 0;

    return (
        <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
            <div className="flex items-center gap-2 mb-4">
                <Hash className="w-5 h-5 text-[#4F200D]" />
                <h3 className="text-lg font-bold text-gray-800">핵심 키워드</h3>
            </div>

            {!hasKeywords && (
                <p className="text-sm text-gray-400">핵심 키워드 데이터가 없습니다.</p>
            )}

            {hasKeywords && (
                <div className="flex flex-wrap gap-2">
                    {keywords.map((item, idx) => (
                        <span
                            key={idx}
                            className="px-3 py-1 bg-[#FFF9C4] text-gray-700 rounded-full text-sm font-medium"
                        >
                            #{item.keyword}
                        </span>
                    ))}
                </div>
            )}
        </section>
    );
}
