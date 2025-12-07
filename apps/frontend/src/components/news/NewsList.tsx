import React from "react";

export interface NewsItem {
    id: string;
    title: string;
    publisher: string;
    publishedAt: string;
    summary?: string;
    sentiment?: "positive" | "negative" | "neutral";
    url?: string;
    content?: string;
}

interface NewsListProps {
    items: NewsItem[];
    selectedId?: string;
    onSelect?: (id: string) => void;
    onRead?: (id: string) => void;
}

const NewsList: React.FC<NewsListProps> = ({ items, selectedId, onSelect, onRead }) => {
    if (!items.length) return <div className="text-gray-500 p-4">관련 뉴스가 없습니다.</div>;

    return (
        <ul className="divide-y divide-gray-200">
            {items.map((n) => {
                const isActive = selectedId === n.id;
                return (
                    <li key={n.id} className={isActive ? "bg-amber-100" : ""}>
                        <div className="p-3">
                            <button
                                type="button"
                                onClick={() => onSelect?.(n.id)}
                                className="w-full text-left hover:bg-amber-50 transition rounded-md p-1"
                                aria-pressed={isActive}
                            >
                                <div className="text-sm text-gray-500 mb-1">
                                    {n.publisher} • {new Date(n.publishedAt).toLocaleString()}
                                </div>
                                <div className="font-semibold line-clamp-2">{n.title}</div>
                                {n.summary && (
                                    <div className="text-sm text-gray-700 line-clamp-2 mt-1">{n.summary}</div>
                                )}
                                {n.sentiment && (
                                    <span
                                        className={`inline-block mt-2 text-xs px-2 py-0.5 rounded ${n.sentiment === "positive"
                                            ? "bg-green-100 text-green-700"
                                            : n.sentiment === "negative"
                                                ? "bg-red-100 text-red-700"
                                                : "bg-gray-100 text-gray-700"
                                            }`}
                                    >
                                        {n.sentiment}
                                    </span>
                                )}
                            </button>

                            <div className="mt-2 flex justify-end">
                                <button
                                    type="button"
                                    onClick={() => onRead?.(n.id)}
                                    className="px-3 py-1 rounded-lg font-semibold text-white transition"
                                    style={{ backgroundColor: "#4F200D" }}
                                >
                                    읽기
                                </button>
                            </div>
                        </div>
                    </li>
                );
            })}
        </ul>
    );
};

export default NewsList;
