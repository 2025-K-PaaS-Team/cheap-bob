import { ProgressBar } from "@components/seller/signup";
import { pages, notProgressBarPages } from "@constant";
import { useState } from "react";

const Signup = () => {
  const [pageIdx, setPageIdx] = useState<number>(0);
  const CurrentPage = pages[pageIdx];
  const isProgressBar = !notProgressBarPages.includes(CurrentPage);

  return (
    <div className="min-h-screen flex flex-col">
      {/* 페이지 내용 */}
      <div className="flex-1">
        {/* progressbar header */}
        {isProgressBar && <ProgressBar pageIdx={pageIdx} />}
        <CurrentPage pageIdx={pageIdx} setPageIdx={setPageIdx} />
      </div>

      {/* 바닥 버튼 영역 */}
      {/* <div className="fixed bottom-4 left-0 w-full px-5 flex gap-2">
        {pageIdx > 1 && (
          <CommonBtn
            label="이전"
            onClick={() => setPageIdx(pageIdx - 1)}
            className="bg-[#EDEDED] text-black border-0"
            width="w-1/3"
            notBottom
          />
        )}

        <CommonBtn
          label="다음"
          onClick={() => setPageIdx(pageIdx + 1)}
          className="bg-black text-white"
          width={pageIdx > 1 ? "w-2/3" : "w-full"}
          notBottom
        />
      </div> */}
    </div>
  );
};

export default Signup;
