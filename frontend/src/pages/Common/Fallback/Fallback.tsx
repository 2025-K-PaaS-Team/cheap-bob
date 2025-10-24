import { CommonBtn } from "@components/common";
import { useNavigate } from "react-router-dom";

const Fallback = () => {
  const navigate = useNavigate();
  const role = localStorage.getItem("loginRole");

  return (
    <div className="flex flex-col flex-1 items-center justify-center text-center mx-auto w-[calc(100%-40px)] gap-y-[28px]">
      <img src="/icon/error.svg" alt="errorIcon" className="w-15 mb-5" />
      <div className="titleFont font-bold">404</div>
      <div className="text-[16px]">
        현재 {role === "customer" ? "고객" : "점주"} 계정으로 로그인이 되어 있는
        것 같아요
        <br />
        {role === "customer" ? "고객" : "점주"} 페이지로 이동하시겠어요?
      </div>
      {role === "customer" ? (
        <CommonBtn
          label="고객 페이지로 이동하기"
          onClick={() => navigate("/c/stores")}
        />
      ) : (
        <CommonBtn
          label="점주 페이지로 이동하기"
          onClick={() => navigate("/s/dashboard")}
          notBottom
        />
      )}
    </div>
  );
};

export default Fallback;
