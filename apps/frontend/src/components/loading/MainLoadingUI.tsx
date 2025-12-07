// src/components/loading/MainLoadingUI.tsx

import { useMemo } from "react";
import logo from "../../assets/logo.svg";
import honeyBg from "../../assets/honeyBgImg.svg";
import beeLeft from "../../assets/beeLeft.svg";
import beeRight from "../../assets/beeRight.svg";
import flower from "../../assets/flower.svg";
import type { LoaderState } from "./useReportLoader";


export default function MainLoadingUI({ progress, currentMessage, cancel }: LoaderState) {

    const animStyle = useMemo(() => ({ animation: "slideUp 480ms ease-out" }), []);

    return (
        <div className="flex flex-col items-center w-full min-h-screen bg-[#FAF9F6]" style={animStyle}>
            {/* 상단 꿀 배경 및 로고 */}
            <div className="relative w-full h-[300px] overflow-hidden">
                <img src={honeyBg} className="absolute inset-x-0 bottom-0 w-full h-auto" />
                <div className="w-full flex justify-start px-6 pt-20 absolute top-0 left-0 z-10">
                    <img src={logo} className="h-10" />
                </div>
            </div>

            <div className="flex-1 w-full flex flex-col items-center pt-30 px-6">
                {/* 벌 애니메이션 영역 */}
                <div className="relative w-full flex items-end justify-center mb-8">
                    <img src={beeLeft} className="h-[80px] mr-4 animate-float-slow" />
                    <img src={flower} className="h-[160px] animate-flower-rotate" />
                    <img src={beeRight} className="h-[80px] ml-4 animate-float-fast" />
                </div>

                {/* 메시지 및 프로그레스 영역 */}
                <div className="text-center mb-5">
                    <div className="text-[20px] font-extrabold text-[#4F200D]">꿀 정보 모으는 중...</div>

                    {/* 순환 메시지 출력 */}
                    <div className="mt-2 text-[12px] text-gray-600 min-h-[18px]">
                        {currentMessage}

                    </div>
                </div>

                {/* 프로그레스 바 */}
                <div className="w-[80%] max-w-[320px] h-2 rounded-full bg-gray-200 overflow-hidden mb-1">
                    <div
                        className="h-full bg-[#FFA000] transition-[width] duration-200 ease-out"
                        style={{ width: `${Math.floor(progress)}%` }}
                    />
                </div>
                <div className="text-xs text-gray-500 mb-6">{Math.floor(progress)}%</div>

                {/* 취소 버튼 */}
                <button onClick={cancel} className="mt-2 px-6 py-2 rounded-full text-white font-semibold shadow-md"
                    style={{ backgroundColor: "#4F200D" }}>
                    취소하기
                </button>
            </div>
        </div>
    );
}