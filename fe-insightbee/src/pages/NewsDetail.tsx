import { useNavigate } from "react-router-dom"

function NewsDetailPage() {
    const navigate = useNavigate()

    return (
        <div className="p-4">
            <button
                className="mb-4 text-amber-600 font-semibold"
                onClick={() => navigate(-1)} // 이전 페이지로
            >
                ← 돌아가기
            </button>
            <h1 className="text-2xl font-bold mb-2">[삼성전자] AI 투자 확대</h1>
            <p className="text-gray-700">
                이곳에 뉴스 전문 내용이 표시됩니다...
            </p>
        </div>
    )
}

export default NewsDetailPage
