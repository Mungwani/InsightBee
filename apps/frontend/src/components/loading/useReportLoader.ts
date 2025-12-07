/* eslint-disable @typescript-eslint/no-explicit-any */
// src/components/loading/useReportLoader.ts

import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchNewsByCompany, fetchSummaryByCompany, fetchKeywordsByCompany, fetchPointsByCompany } from "../../services/report/getReport"; 

// 멘트 목록 정의
const startMessage = "벌들이 뉴스를 분석하고 있습니다!";
const middleMessages = [
    "키워드를 꼼꼼하게 추출 중이에요!",
    "요약 문장을 정리하고 있어요.",
    "정보가 꿀처럼 모이고 있어요!",
];
const endMessage = "잠시만 기다려주시면 리포트가 완성돼요.";

const MESSAGE_DISPLAY_TIME = 1500;
const FINAL_PROGRESS_TIME = 1100;

export interface LoaderState {
    progress: number;
    currentMessage: string;
    company: string;
    cancel: () => void;
}

export const useReportLoader = (company: string): LoaderState => {
    const navigate = useNavigate();
    
    // UI 상태
    const [progress, setProgress] = useState(0);
    const [currentMessage, setCurrentMessage] = useState(startMessage);

    // 내부 상태 및 참조
    const rafRef = useRef<number | null>(null);
    const intervalRef = useRef<number | null>(null);
    const isNavigated = useRef(false);
    const apiCompleted = useRef(false);
    const messageStep = useRef(0);

    // 캔슬 함수 (로딩 중단)
    const cancel = () => {
        console.log("🛑 취소하기 실행 — 메인으로 이동");
        isNavigated.current = true;
        if (rafRef.current) cancelAnimationFrame(rafRef.current);
        if (intervalRef.current) clearInterval(intervalRef.current);
        navigate("/main", { replace: true });
    };

    // 메시지 순환 및 반복 로직
    useEffect(() => {
        const updateMessage = () => {
            messageStep.current += 1;
            
            if (apiCompleted.current) {
                if (messageStep.current >= 2) { 
                    setCurrentMessage(endMessage);
                    if (intervalRef.current) clearInterval(intervalRef.current);
                    return;
                }
            }
            
            // 중간 멘트 (API 완료 전까지 반복)
            const randomIndex = Math.floor(Math.random() * middleMessages.length);
            setCurrentMessage(middleMessages[randomIndex]);
        };

        setCurrentMessage(startMessage);
        messageStep.current = 0;

        intervalRef.current = window.setInterval(updateMessage, MESSAGE_DISPLAY_TIME);

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, []);

    // 프로그레스 바 애니메이션 및 API 호출 로직
    useEffect(() => {
        if (!company) {
            console.log("❗ 회사명 없음. API 호출 중단");
            return;
        }

        // 90% 이후의 속도를 조정하는 함수
        const animateFinalProgress = (startTime: number) => {
            const duration = FINAL_PROGRESS_TIME;
            const frame = (timestamp: number) => {
                const elapsed = timestamp - startTime;
                const finalProgress = Math.min(90 + (elapsed / duration) * 10, 100);
                setProgress(finalProgress);

                if (finalProgress < 100 && !isNavigated.current) {
                    rafRef.current = requestAnimationFrame(frame);
                }
            };
            rafRef.current = requestAnimationFrame(frame);
        };

        // 0%에서 90%까지의 초기 애니메이션
        const startAnimation = () => {
            const animate = () => {
                setProgress(prev => {
                    if (apiCompleted.current && prev >= 90) return 90;
                    if (prev >= 90) return prev + (99 - prev) * 0.001; 
                    
                    let increment = (90 - prev) * 0.015; 
                    increment = Math.min(increment, 0.4); 
                    return prev + increment;
                });

                if (!isNavigated.current) {
                    rafRef.current = requestAnimationFrame(animate);
                }
            };
            rafRef.current = requestAnimationFrame(animate);
        };

        startAnimation();

        // API 호출 시작 로그 추가 (useEffect 진입 시점에 가까움)
        console.log(`[LOADER DEBUG] API 호출 시작: ${company}`);

        async function loadAll() {
            try {
                const timerPromise = new Promise((resolve) => setTimeout(resolve, 3000));
                
                // 1. 모든 API 호출을 변수에 할당하여 시작
                const summaryPromise = fetchSummaryByCompany(company);
                const newsPromise = fetchNewsByCompany(company);
                const keywordsPromise = fetchKeywordsByCompany(company);
                const pointsPromise = fetchPointsByCompany(company); 
                
                console.log("[LOADER DEBUG] Points API 호출 준비 완료.");
                
                const apiPromise = Promise.all([
                    summaryPromise,
                    newsPromise,
                    keywordsPromise,
                    pointsPromise,
                ]);

                const [, apiResults] = await Promise.all([timerPromise, apiPromise]);
                
                // 2. 결과 할당에 'points' 추가
                const [summary, news, keywords, points] = apiResults; 

                console.log("[LOADER DEBUG] 모든 API 완료.");
                console.log("-> Summary:", summary);
                console.log("-> Points:", points); // 이 로그를 확인해야 합니다.

                const isSummaryEmpty = !summary || (typeof summary === "object" && Object.keys(summary).length === 0);
                const isNewsEmpty = !news || (Array.isArray(news) && news.length === 0);

                if (isSummaryEmpty && isNewsEmpty) {
                    throw { status: 404 };
                }
                
                // API 완료 플래그 설정 및 메시지 전환 준비
                apiCompleted.current = true;
                messageStep.current = 1; 

                if (!isNavigated.current) {
                    if (rafRef.current) cancelAnimationFrame(rafRef.current);
                    
                    // 90% -> 100% 애니메이션 시작
                    animateFinalProgress(performance.now());
                    
                    setTimeout(() => {
                        if (!isNavigated.current) {
                            isNavigated.current = true;

                            navigate(`/report/${encodeURIComponent(company)}`, {
                                replace: true,
                                // 3. points 데이터를 state에 추가
                                state: { summary, news, keywords, points }, 
                            });
                        }
                    }, FINAL_PROGRESS_TIME + 200);
                }

            } catch (e: any) {
                console.error("❌ MainLoading 오류 발생:", e);
                // ... (에러 처리 로직 유지)
                if (!isNavigated.current) {
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
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
            if (intervalRef.current) clearInterval(intervalRef.current);
        };

    }, [navigate, company]);

    return { progress, currentMessage, company, cancel };
};