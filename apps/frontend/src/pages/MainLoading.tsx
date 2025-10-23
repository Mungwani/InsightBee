import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import logo from "../assets/logo.svg";
import honeyBg from "../assets/honeyBgImg.svg";
import beeLeft from "../assets/beeLeft.svg";
import beeRight from "../assets/beeRight.svg";
import flower from "../assets/flower.svg";

export default function MainLoading() {
    const navigate = useNavigate();
    const { state } = useLocation() as { state?: { company?: string } };
    const company = state?.company ?? "";

    const [progress, setProgress] = useState(0);
    const rafRef = useRef<number | null>(null);
    const doneRef = useRef(false);

    // 5초 진행 후 /report로 이동
    useEffect(() => {
        const start = performance.now();
        const duration = 5000;

        const tick = (now: number) => {
            const p = Math.min(1, (now - start) / duration);
            setProgress(Math.floor(p * 100));
            if (p < 1 && !doneRef.current) {
                rafRef.current = requestAnimationFrame(tick);
            } else if (!doneRef.current) {
                doneRef.current = true;
                navigate("/report", { replace: true, state: { company } });
            }
        };
        rafRef.current = requestAnimationFrame(tick);

        return () => {
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, [navigate, company]);

    const cancel = () => {
        doneRef.current = true;
        if (rafRef.current) cancelAnimationFrame(rafRef.current);
        navigate("/main", { replace: true });
    };

    // 첫 진입 슬라이드 업
    const animStyle = useMemo(() => ({ animation: "slideUp 480ms ease-out" }), []);

    return (
        <div
            className="relative flex flex-col items-center w-full min-h-screen bg-[#FAF9F6] overflow-hidden"
            style={animStyle}
        >
            {/* keyframes */}
            <style>{`
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>

            {/* 꿀 배경 드립 */}
            <img
                src={honeyBg}
                alt="honey background"
                className="absolute top-0 left-0 w-full h-auto pointer-events-none select-none"
            />

            {/* 상단 로고 */}
            <div className="w-full flex justify-start px-6 pt-6 relative z-10">
                <img src={logo} alt="InsightBee Logo" className="h-8" />
            </div>

            {/* 일러스트 */}
            <div className="relative mt-28 z-10 flex items-end justify-center">
                <img src={beeLeft} alt="Bee Left" className="h-[80px] mr-4" />
                <img src={flower} alt="Flower" className="h-[160px]" />
                <img src={beeRight} alt="Bee Right" className="h-[80px] ml-4" />
            </div>

            {/* 텍스트 */}
            <div className="mt-8 text-center relative z-10">
                <div
                    className="text-[20px] font-extrabold text-[#4F200D]"
                    style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
                >
                    꿀 정보 모으는 중..
                </div>
                <div className="mt-2 text-[12px] text-gray-600">
                    벌들이 열심히 최신 뉴스를 수집하고 분석하고 있습니다.
                    {company ? <span className="ml-1 text-[#4F200D] font-semibold">({company})</span> : null}
                </div>
            </div>

            {/* 진행 바 */}
            <div className="mt-5 w-[80%] max-w-[320px] h-2 rounded-full bg-gray-200 overflow-hidden shadow-inner">
                <div
                    className="h-full bg-[#FFA000] transition-[width] duration-150 ease-out"
                    style={{ width: `${progress}%` }}
                />
            </div>
            <div className="mt-1 text-xs text-gray-500">{progress}%</div>

            {/* 취소 버튼 */}
            <button
                onClick={cancel}
                className="mt-6 px-6 py-2 rounded-full text-white font-semibold shadow-md"
                style={{ backgroundColor: "#4F200D" }}
            >
                취소하기
            </button>
        </div>
    );
}
