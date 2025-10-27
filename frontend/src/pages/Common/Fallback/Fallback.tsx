import { CommonBtn } from "@components/common";
import { useNavigate } from "react-router-dom";

const Fallback = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col flex-1 items-center justify-center text-center mx-auto w-[calc(100%-40px)] gap-y-[28px]">
      <img src="/icon/error.svg" alt="errorIcon" className="w-15 mb-5" />
      <div className="titleFont font-bold">404</div>
      <div className="text-[16px]">
        페이지를 찾을 수 없습니다. 아래 버튼을 눌러 홈으로 돌아가세요.
      </div>

      <div className="flex flex-col w-full gap-y-[10px">
        <CommonBtn
          label="고객 페이지로 이동하기"
          onClick={() => navigate("/c/stores")}
        />
        <CommonBtn
          label="점주 페이지로 이동하기"
          onClick={() => navigate("/s/dashboard")}
          notBottom
        />
      </div>
    </div>
  );
};

export default Fallback;
