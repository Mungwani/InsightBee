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

    // 5초 후 /report 이동
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

    const animStyle = useMemo(() => ({ animation: "slideUp 480ms ease-out" }), []);

    return (
        <div
            className="flex flex-col items-center w-full min-h-screen bg-[#FAF9F6]"
            style={animStyle}
        >
            {/* 🔶 상단 노란 드립 영역 (여기까지만 노란색!) */}
            <div className="relative w-full h-[400px] overflow-hidden">
                {/* 드립 이미지는 이 영역 안에서만 */}
                <img
                    src={honeyBg}
                    alt="honey background"
                    className="absolute inset-x-0 bottom-0 w-full h-auto pointer-events-none"
                />

                {/* 로고 (메인과 동일한 위치) */}
                <div className="w-full flex justify-start px-6 pt-20 absolute top-0 left-0 z-10">
                    <img src={logo} alt="InsightBee Logo" className="h-10" />
                </div>

            </div>

            {/* 🔽 여기부터는 전부 흰 배경 영역 (벌/꽃/텍스트/바/버튼) */}
            <div className="flex-1 w-full flex flex-col items-center pt-10 px-6">
                {/* 벌 + 꽃 (흰 배경 위!) */}
                <div className="relative w-full flex items-end justify-center mb-8">
                    <img
                        src={beeLeft}
                        alt="Bee Left"
                        className="h-[80px] mr-4 animate-float-slow"
                    />
                    <img
                        src={flower}
                        alt="Flower"
                        className="h-[160px] animate-flower-rotate"
                    />
                    <img
                        src={beeRight}
                        alt="Bee Right"
                        className="h-[80px] ml-4 animate-float-fast"
                    />
                </div>

                {/* 텍스트 */}
                <div className="text-center mb-5">
                    <div className="text-[20px] font-extrabold text-[#4F200D]">
                        꿀 정보 모으는 중...
                    </div>
                    <div className="mt-2 text-[12px] text-gray-600">
                        벌들이 열심히 최신 뉴스를 수집하고 분석하고 있습니다.
                        {company && (
                            <span className="ml-1 text-[#4F200D] font-semibold">
                                ({company})
                            </span>
                        )}
                    </div>
                </div>

                {/* 로딩 바 */}
                <div className="w-[80%] max-w-[320px] h-2 rounded-full bg-gray-200 overflow-hidden mb-1">
                    <div
                        className="h-full bg-[#FFA000] transition-[width] duration-200 ease-out"
                        style={{ width: `${progress}%` }}
                    />
                </div>
                <div className="text-xs text-gray-500 mb-6">{progress}%</div>

                {/* 취소 버튼 */}
                <button
                    onClick={cancel}
                    className="mt-2 px-6 py-2 rounded-full text-white font-semibold shadow-md"
                    style={{ backgroundColor: "#4F200D" }}
                >
                    취소하기
                </button>
            </div>
        </div>
    );
}
