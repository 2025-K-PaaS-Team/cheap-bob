import { ProgressBar } from "@components/seller/signup";
import { pages, notProgressBarPages } from "@constant";
import { useState } from "react";

const Signup = () => {
  const [pageIdx, setPageIdx] = useState<number>(0);
  const CurrentPage = pages[pageIdx];
  const isProgressBar = !notProgressBarPages.includes(CurrentPage);

  return (
    <div className="min-h-screen flex flex-col">
      {/* page content */}
      <div className="flex-1">
        {/* progressbar header */}
        {isProgressBar && <ProgressBar pageIdx={pageIdx} />}
        <CurrentPage pageIdx={pageIdx} setPageIdx={setPageIdx} />
      </div>
    </div>
  );
};

export default Signup;
