export default function NewsCard() {
  return (
    <div className="flex flex-col gap-4 text-black border border-gray-200 rounded-2xl p-[10px]">
      <div className="flex justify-between">
        <div className="w-[80%]"> 제목</div>
        <div>긍정</div>
      </div>

      <div className="text-sm text-gray-400">요약</div>
      <div className="flex justify-between items-center">
        {/* 왼쪽 */}
        <div className="flex gap-2 text-xs">
          <div className="flex gap-1">
            <div>사</div>
            <div>연합뉴스</div>
          </div>
          <div className="flex gap-1">
            <div>진</div>
            <div>1202-12-31 </div>
          </div>
        </div>
        {/* 오른쪽 버튼 */}
        <div className="flex text-[11px] gap-1">
          <button className="w-[70px] h-[30px] !bg-white">북마크</button>
        </div>
      </div>
    </div>
  );
}
