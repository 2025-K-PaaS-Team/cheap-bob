import { ProgressBar } from "@components/seller/signup";
import { useState } from "react";
import { RegisterName } from "./StoreInfo";

const Signup = () => {
  const [pageIdx, setPageIdx] = useState<number>(0);

  return (
    <div className="">
      <ProgressBar pageIdx={pageIdx} />
      <RegisterName />
    </div>
  );
};

export default Signup;
