import HashTag from "./HashTag";

export default function NewsCard() {
  return (
    <div className="flex flex-col gap-4 text-black border-1 border-gray-200 rounded-2xl p-[10px]">
      <div className="flex justify-between">
        <div className="w-[80%]">3분기 실적 발표</div>
        <div>긍정</div>
      </div>

      <div className="text-sm text-gray-400">
        매출 39억원으로 어쩌구 저쩌구 주식 올라라
      </div>
      <button className="!bg-white text-gray-400 !text-xs w-[80px] !p-0">
        📄 45개 기사
      </button>
      <HashTag />
    </div>
  );
}
