// src/pages/Main.tsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.svg";
import honeyBg from "../assets/honeyBgImg.svg";
import beeLeft from "../assets/beeLeft.svg";
import beeRight from "../assets/beeRight.svg";
import flower from "../assets/flower.svg";

export default function Main() {
    const [q, setQ] = useState("");
    const [suggestions, setSuggestions] = useState<
        { company_id: number; name_ko: string }[]
    >([]);
    const [showList, setShowList] = useState(false);

    const navigate = useNavigate();

    /**  검색 시작 */
    const goLoading = (e: React.FormEvent) => {
        e.preventDefault();
        const query = q.trim();
        if (!query) return;
        navigate("/main-loading", { state: { company: query } });
    };

    /**  자동완성 API */
    useEffect(() => {
        if (!q.trim()) {
            setSuggestions([]);
            setShowList(false);
            return;
        }

        const timer = setTimeout(async () => {
            try {
                const res = await fetch(
                    `/api/companies?query=${encodeURIComponent(q)}`
                );
                const json = await res.json();

                if (Array.isArray(json)) {
                    setSuggestions(json.slice(0, 10)); // 최대 10건
                    setShowList(true);
                }
            } catch (err) {
                console.error("자동완성 오류:", err);
            }
        }, 150);

        return () => clearTimeout(timer);
    }, [q]);

    return (
        <div className="relative flex flex-col items-center w-full min-h-screen bg-[#FAF9F6] overflow-hidden">
            <img src={honeyBg} alt="honey background" className="absolute top-0 left-0 w-full h-auto" />

            {/* 로고 */}
            <div className="w-full flex justify-start px-6 pt-20 relative z-10">
                <img src={logo} alt="InsightBee Logo" className="h-10" />
            </div>

            {/* 타이틀 */}
            <h1 className="mt-12 relative z-10 font-extrabold text-[29px] text-[#4F200D]"
                style={{ fontFamily: "'Noto Sans KR', sans-serif" }}>
                뉴스로 보는 기업 인사이트
            </h1>

            {/* 검색 박스 */}
            <form onSubmit={goLoading} className="mt-6 w-80 bg-white rounded-2xl shadow-md p-4 flex flex-col items-center relative z-10">
                <div className="flex items-center w-full border border-[#8B5E3C] rounded-lg px-3 py-2 relative">
                    <span className="text-[#8B5E3C] mr-2">🔍</span>
                    <input
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                        onBlur={() => setTimeout(() => setShowList(false), 150)}
                        type="text"
                        placeholder="기업명을 입력하세요"
                        className="flex-1 outline-none text-gray-700 placeholder:text-[#8B5E3C]"
                    />

                    {/*  자동완성 리스트 */}
                    {showList && suggestions.length > 0 && (
                        <ul
                            className="absolute top-[48px] left-0 w-full bg-white border border-[#8B5E3C] rounded-lg shadow-lg z-20 max-h-60 overflow-y-auto"
                        >
                            {suggestions.map((item) => (
                                <li
                                    key={item.company_id}
                                    onMouseDown={() => {
                                        setQ(item.name_ko);
                                        setShowList(false);
                                    }}
                                    className="px-3 py-2 hover:bg-[#FFF3D6] cursor-pointer text-[#4F200D]"
                                >
                                    {item.name_ko}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>

                <button type="submit"
                    className="mt-4 bg-[#4F200D] text-white px-6 py-2 rounded-lg font-semibold hover:bg-[#3E1E04] transition">
                    분석 시작
                </button>
            </form>

            {/* 벌 + 꽃 전체 영역 */}
            <div className="relative w-full h-[430px] mt-20 z-10 pointer-events-none">

                {/* 왼쪽 벌 */}
                <img
                    src={beeLeft}
                    alt="left bee"
                    className="absolute left-6 bottom-[60px] h-[90px] animate-float-slow"
                />

                {/* 꽃 (정중앙 아래로 더 내림) */}
                <div className="absolute left-1/2 bottom-[-10px] -translate-x-1/2">
                    <img
                        src={flower}
                        alt="Flower"
                        className="h-[180px] animate-flower-rotate"
                    />
                </div>

                {/* 오른쪽 벌 */}
                <img
                    src={beeRight}
                    alt="right bee"
                    className="absolute right-6 bottom-[100px] h-[90px] animate-float-fast"
                />
            </div>


        </div>
    );
}
