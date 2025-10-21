import { CommonBtn } from "@components/common";
import { useNavigate } from "react-router";

const LoginFail = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col flex-1 items-center justify-center text-center mx-auto w-[calc(100%-40px)] gap-y-[28px]">
      <img src="/icon/error.svg" alt="errorIcon" className="w-15 mb-5" />
      <div className="titleFont font-bold">로그인에 실패했어요</div>
      <div className="text-[16px]">
        점주와 고객 계정은 중복 가입이 불가능합니다.
        <br />
        로그인할 계정을 선택해주세요.
      </div>

      <div className="flex flex-col gap-y-[20px] my-[20px] w-full">
        <CommonBtn
          label="점주 로그인하기"
          onClick={() => navigate("/s")}
          notBottom
        />
        <CommonBtn
          label="고객 로그인하기"
          notBottom
          onClick={() => navigate("/c")}
        />
      </div>
    </div>
  );
};

export default LoginFail;
