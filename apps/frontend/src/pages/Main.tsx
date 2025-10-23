// src/pages/Main.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.svg";
import honeyBg from "../assets/honeyBgImg.svg";
import beeLeft from "../assets/beeLeft.svg";
import beeRight from "../assets/beeRight.svg";
import flower from "../assets/flower.svg";

export default function Main() {
    const [q, setQ] = useState("");
    const navigate = useNavigate();

    const goLoading = (e: React.FormEvent) => {
        e.preventDefault();
        const query = q.trim();
        if (!query) return;
        navigate("/main-loading", { state: { company: query } });
    };

    return (
        <div className="relative flex flex-col items-center w-full min-h-screen bg-[#FAF9F6] overflow-hidden">
            <img src={honeyBg} alt="honey background" className="absolute top-0 left-0 w-full h-auto" />

            {/* 로고 */}
            <div className="w-full flex justify-start px-6 pt-20 relative z-10">
                <img src={logo} alt="InsightBee Logo" className="h-10" />
            </div>

            {/* 타이틀 */}
            <h1 className="mt-12 relative z-10 font-extrabold text-[29px] text-[#4F200D]" style={{ fontFamily: "'Noto Sans KR', sans-serif" }}>
                뉴스로 보는 기업 인사이트
            </h1>

            {/* 검색 박스 */}
            <form onSubmit={goLoading} className="mt-6 w-80 bg-white rounded-2xl shadow-md p-4 flex flex-col items-center relative z-10">
                <div className="flex items-center w-full border border-[#8B5E3C] rounded-lg px-3 py-2">
                    <span className="text-[#8B5E3C] mr-2">🔍</span>
                    <input
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                        type="text"
                        placeholder="기업명을 입력하세요"
                        className="flex-1 outline-none text-gray-700 placeholder:text-[#8B5E3C]"
                    />
                </div>
                <button type="submit" className="mt-4 bg-[#4F200D] text-white px-6 py-2 rounded-lg font-semibold hover:bg-[#3E1E04] transition">
                    분석 시작
                </button>
            </form>

            {/* 벌 + 꽃 */}
            <div className="flex justify-center mt-20 relative z-10">
                <div className="mx-6 self-end">
                    <img src={beeLeft} alt="Bee Left" className="h-[100px]" />
                </div>
                <div className="mx-6 mt-60">
                    <img src={flower} alt="Flower" className="h-[200px]" />
                </div>
                <div className="mx-6 self-end">
                    <img src={beeRight} alt="Bee Right" className="h-[100px]" />
                </div>
            </div>
        </div>
    );
}

