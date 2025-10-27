import { CommonBtn } from "@components/common";
import { useNavigate } from "react-router-dom";
import Lottie from "lottie-react";
import information from "@assets/information.json";

const LoginFail = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col flex-1 items-center justify-center text-center mx-auto w-[calc(100%-40px)] gap-y-[20px]">
      <Lottie
        animationData={information}
        style={{ width: "150px", height: "150px" }}
      />
      <div className="titleFont font-bold">로그인에 실패했어요</div>
      <div className="text-[16px]">
        점주와 고객 계정은 중복 가입이 불가능합니다.
        <br />
        로그인할 계정을 선택해주세요.
      </div>
      <div className="flex flex-col w-full gap-y-[10px]">
        <CommonBtn
          label="고객 페이지로 이동하기"
          onClick={() => navigate("/c")}
          notBottom
        />
        <CommonBtn
          label="점주 페이지로 이동하기"
          onClick={() => navigate("/s")}
          notBottom
        />
      </div>
    </div>
  );
};

export default LoginFail;
