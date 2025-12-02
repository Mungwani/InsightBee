import { useNavigate } from "react-router-dom";

interface ReportHeaderProps {
    title: string;
}

function ReportHeader({ title }: ReportHeaderProps) {
    const navigate = useNavigate();
    return (
        <header className="relative w-full h-[130px]">
            <div className="absolute top-0 left-0 w-full h-[130px] bg-[#FED733] " />
            <div className="absolute left-1/2 top-[66px] w-full h-[135px] bg-[#FED733] rounded-b-[70%] -translate-x-1/2" />
            <div className="relative flex items-center justify-center pt-[54px] px-6 z-10">
                <button
                    onClick={() => navigate(-1)}
                    className="absolute left-6 text-[#4F200D] text-[24px] font-bold"
                >
                    ←
                </button>
                <h1
                    className="font-[700] text-[25px] leading-[30px] text-[#4F200D]"
                    style={{ fontFamily: "'Noto Sans KR', sans-serif" }}
                >
                    {title}
                </h1>
            </div>
        </header>
    );
}

export default ReportHeader; 
