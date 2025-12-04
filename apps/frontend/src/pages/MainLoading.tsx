/* eslint-disable @typescript-eslint/no-explicit-any */
// src/pages/MainLoading.tsx
import { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import logo from "../assets/logo.svg";
import honeyBg from "../assets/honeyBgImg.svg";
import beeLeft from "../assets/beeLeft.svg";
import beeRight from "../assets/beeRight.svg";
import flower from "../assets/flower.svg";
import { fetchNewsByCompany, fetchSummaryByCompany, fetchKeywordsByCompany } from "../services/report/getReport";

export default function MainLoading() {
    const navigate = useNavigate();
    const { state } = useLocation() as { state?: { company?: string } };
    const company = state?.company ?? "";

    const [progress, setProgress] = useState(0);
    const rafRef = useRef<number | null>(null);
    const isNavigated = useRef(false);
    // const isApiCalled = useRef(false); // API 중복 호출 방지 (useRef를 사용하여 StrictMode에서만 사용)

    useEffect(() => {
        if (!company) {
            console.log("❗ 회사명 없음. API 호출 중단");
            return;
        }

        // API 중복 호출 방지 로직 (StrictMode 대응)
        // if (isApiCalled.current) return;
        // isApiCalled.current = true;

        const startAnimation = () => {
            const animate = () => {
                setProgress(prev => {
                    if (prev >= 90) return prev + (99 - prev) * 0.001;
                    let increment = (90 - prev) * 0.01;
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

        // API 호출 및 최소 로딩 시간(3초) 확보 로직
        async function loadAll() {
            try {
                // [1] 최소 3초 대기 Promise
                const timerPromise = new Promise((resolve) => setTimeout(resolve, 3000));

                // [2] 실제 API 호출 Promise
                const apiPromise = Promise.all([
                    fetchSummaryByCompany(company),
                    fetchNewsByCompany(company),
                    fetchKeywordsByCompany(company),
                ]);

                // [3] 타이머와 API 호출 중 늦게 끝나는 것을 기다림 (최소 3초 로딩 보장)
                //      (쉼표(,)는 타이머 결과(void)를 무시하는 destructuring 문법)
                const [, apiResults] = await Promise.all([timerPromise, apiPromise]);
                const [summary, news, keywords] = apiResults;

                const isSummaryEmpty = !summary || (typeof summary === "object" && Object.keys(summary).length === 0);
                const isNewsEmpty = !news || (Array.isArray(news) && news.length === 0);

                if (isSummaryEmpty && isNewsEmpty) {
                    console.log("❗ Summary & News 모두 빈 값. 404 처리");
                    throw { status: 404 };
                }

                if (!isNavigated.current) {

                    if (rafRef.current) cancelAnimationFrame(rafRef.current);
                    setProgress(100); // 로딩바 완료

                    setTimeout(() => {
                        if (!isNavigated.current) {
                            isNavigated.current = true;

                            // 데이터와 함께 Report 페이지로 이동 (이중 호출 방지)
                            navigate(`/report/${encodeURIComponent(company)}`, {
                                replace: true,
                                state: { summary, news, keywords },
                            });
                        }
                    }, 500);
                }

            } catch (e: any) {
                console.error("❌ MainLoading 오류 발생:", e);

                if (!isNavigated.current) {
                    // 에러 메시지 출력
                    if (e.status === 404 || e.response?.status === 404) {
                        alert(`'${company}'에 대한 데이터가 존재하지 않습니다.\n기업명을 다시 확인해 주세요.`);
                    } else {
                        alert(`'${company}' 데이터를 불러오는 중 오류가 발생했습니다.`);
                    }
                    cancel();
                }
            }
        }

        loadAll();

        return () => {
            console.log("🔄 MainLoading cleanup 실행");
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };

    }, [navigate, company]);

    const cancel = () => {
        console.log("🛑 취소하기 실행 — 메인으로 이동");
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