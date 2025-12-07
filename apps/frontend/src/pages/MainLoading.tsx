// src/pages/MainLoading.tsx 

/* eslint-disable @typescript-eslint/no-explicit-any */
import { useLocation } from "react-router-dom";
import MainLoadingUI from "../components/loading/MainLoadingUI";
import { useReportLoader } from "../components/loading/useReportLoader";

export default function MainLoading() {
    const { state } = useLocation() as { state?: { company?: string } };
    const company = state?.company ?? "";

    // 커스텀 훅을 호출하여 로딩 상태와 로직을 가져옵니다.
    const loaderState = useReportLoader(company);

    // UI 컴포넌트에 상태를 전달합니다.
    return (
        <MainLoadingUI {...loaderState} />
    );
}