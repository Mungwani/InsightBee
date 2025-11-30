// src/pages/MainLoading.tsx
import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import logo from "../assets/logo.svg";
import honeyBg from "../assets/honeyBgImg.svg";
import beeLeft from "../assets/beeLeft.svg";
import beeRight from "../assets/beeRight.svg";
import flower from "../assets/flower.svg";
import { fetchNewsByCompany, fetchSummaryByCompany } from "../services/report/getReport";

export default function MainLoading() {
    const navigate = useNavigate();
    const { state } = useLocation() as { state?: { company?: string } };
    const company = state?.company ?? "";

    const [progress, setProgress] = useState(0);
    const rafRef = useRef<number | null>(null);
    const isNavigated = useRef(false);

    // 로딩 + 데이터 병렬 호출
    useEffect(() => {
        if (!company) return;

        /* API 미리 불러오기 */
        async function loadAll() {
            try {
                const [summary, news] = await Promise.all([
                    fetchSummaryByCompany(company),
                    fetchNewsByCompany(company),
                ]);

                if (!isNavigated.current) {
                    navigate(`/report/${encodeURIComponent(company)}`, {
                        replace: true,
                        state: { summary, news },
                    });
                }
            } catch (e) {
                console.error("로딩 실패:", e);
            }
        }

        loadAll();

        /* 로딩 progress 애니메이션 */
        const start = performance.now();
        const duration = 8000;

        const tick = (now: number) => {
            const p = Math.min(1, (now - start) / duration);
            setProgress(Math.floor(p * 100));

            if (p < 1 && !isNavigated.current) {
                rafRef.current = requestAnimationFrame(tick);
            }
        };

        rafRef.current = requestAnimationFrame(tick);

        return () => {
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, [navigate, company]);

    const cancel = () => {
        isNavigated.current = true;
        if (rafRef.current) cancelAnimationFrame(rafRef.current);
        navigate("/main", { replace: true });
    };

    const animStyle = useMemo(() => ({ animation: "slideUp 480ms ease-out" }), []);

    return (
        <div className="flex flex-col items-center w-full min-h-screen bg-[#FAF9F6]" style={animStyle}>
            <div className="relative w-full h-[300px] overflow-hidden">
                <img src={honeyBg} className="absolute inset-x-0 bottom-0 w-full h-auto" />

                <div className="w-full flex justify-start px-6 pt-20 absolute top-0 left-0 z-10">
                    <img src={logo} className="h-10" />
                </div>
            </div>

            <div className="flex-1 w-full flex flex-col items-center pt-30 px-6">
                <div className="relative w-full flex items-end justify-center mb-8">
                    <img src={beeLeft} className="h-[80px] mr-4 animate-float-slow" />
                    <img src={flower} className="h-[160px] animate-flower-rotate" />
                    <img src={beeRight} className="h-[80px] ml-4 animate-float-fast" />
                </div>

                <div className="text-center mb-5">
                    <div className="text-[20px] font-extrabold text-[#4F200D]">꿀 정보 모으는 중...</div>
                    <div className="mt-2 text-[12px] text-gray-600">
                        벌들이 뉴스를 분석하고 있습니다.
                        {company && <span className="ml-1 text-[#4F200D] font-semibold">({company})</span>}
                    </div>
                </div>

                <div className="w-[80%] max-w-[320px] h-2 rounded-full bg-gray-200 overflow-hidden mb-1">
                    <div
                        className="h-full bg-[#FFA000] transition-[width] duration-200 ease-out"
                        style={{ width: `${progress}%` }}
                    />
                </div>
                <div className="text-xs text-gray-500 mb-6">{progress}%</div>

                <button onClick={cancel} className="mt-2 px-6 py-2 rounded-full text-white font-semibold shadow-md"
                    style={{ backgroundColor: "#4F200D" }}>
                    취소하기
                </button>
            </div>
        </div>
    );
}
