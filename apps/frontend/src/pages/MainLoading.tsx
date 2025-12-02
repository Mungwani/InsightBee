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

    useEffect(() => {
        if (!company) return;

        // 1. 애니메이션 시작 (최대 90%까지만 천천히 증가)
        // useEffect 내부

        // 1. 애니메이션 시작
        const startAnimation = () => {
            const animate = () => {
                setProgress((prev) => {
                    // 90% 이상이면 거의 멈춤 (아주 미세하게만 증가)
                    if (prev >= 90) {
                        return prev + (99 - prev) * 0.001;
                    }

                    // [수정된 부분]
                    // 속도 계산: 남은 거리의 1% (기존 5%에서 줄임)
                    let increment = (90 - prev) * 0.01;

                    // [핵심] 초반 급발진 방지: 한 프레임당 최대 0.2%까지만 오르도록 제한
                    // 이렇게 하면 초반에도 0.2%씩 꾸준히 오르다가, 
                    // 나중에 0.2보다 작아지면 자연스럽게 느려집니다.
                    increment = Math.min(increment, 0.2);

                    return prev + increment;
                });

                if (!isNavigated.current) {
                    rafRef.current = requestAnimationFrame(animate);
                }
            };
            rafRef.current = requestAnimationFrame(animate);
        };

        startAnimation();

        // 2. API 호출
        async function loadAll() {
            try {
                const [summary, news] = await Promise.all([
                    fetchSummaryByCompany(company),
                    fetchNewsByCompany(company),
                ]);

                if (!isNavigated.current) {
                    // API 완료 시 애니메이션 중단하고 100%로 점프
                    if (rafRef.current) cancelAnimationFrame(rafRef.current);
                    setProgress(100);

                    // 사용자가 100% 찬 것을 인지할 수 있게 0.5초 딜레이 후 이동
                    setTimeout(() => {
                        if (!isNavigated.current) {
                            navigate(`/report/${encodeURIComponent(company)}`, {
                                replace: true,
                                state: { summary, news },
                            });
                            isNavigated.current = true;
                        }
                    }, 500);
                }
            } catch (e) {
                console.error("로딩 실패:", e);
                // 에러 처리 (필요시 알림 표시 후 메인으로 등)
                cancel();
            }
        }

        loadAll();

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
                        // Math.floor로 소수점 제거하여 CSS에 적용
                        style={{ width: `${Math.floor(progress)}%` }}
                    />
                </div>
                <div className="text-xs text-gray-500 mb-6">{Math.floor(progress)}%</div>

                <button onClick={cancel} className="mt-2 px-6 py-2 rounded-full text-white font-semibold shadow-md"
                    style={{ backgroundColor: "#4F200D" }}>
                    취소하기
                </button>
            </div>
        </div>
    );
}