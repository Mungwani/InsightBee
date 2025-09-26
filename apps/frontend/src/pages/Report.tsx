import { useState } from "react"
import { useNavigate } from "react-router-dom"

function ReportPage() {
    const [tab, setTab] = useState<"keyword" | "interview">("keyword")
    const navigate = useNavigate()

    return (
        <div className="flex flex-col h-screen">
            {/* TabNav */}
            <div className="flex border-b bg-white">
                <button
                    className={`flex-1 py-3 ${tab === "keyword" ? "border-b-2 border-amber-500 font-bold" : ""}`}
                    onClick={() => setTab("keyword")}
                >
                    키워드
                </button>
                <button
                    className={`flex-1 py-3 ${tab === "interview" ? "border-b-2 border-amber-500 font-bold" : ""}`}
                    onClick={() => setTab("interview")}
                >
                    면접
                </button>
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto p-4 bg-yellow-50">
                {tab === "keyword" && (
                    <div>
                        <h2 className="text-lg font-bold mb-2">키워드 분석</h2>
                        <div
                            className="p-3 border rounded mb-2 cursor-pointer hover:bg-amber-50"
                            onClick={() => navigate("/report/keyword/news-detail")}
                        >
                            <p className="font-semibold">[삼성전자] AI 투자 확대</p>
                            <p className="text-sm text-gray-600">최근 3개월 핵심 뉴스</p>
                        </div>
                    </div>
                )}

                {tab === "interview" && (
                    <div>
                        <h2 className="text-lg font-bold mb-2">면접 질문/답변</h2>
                        <p>AI가 추천하는 예상 질문과 답변이 여기에 표시됩니다.</p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default ReportPage
