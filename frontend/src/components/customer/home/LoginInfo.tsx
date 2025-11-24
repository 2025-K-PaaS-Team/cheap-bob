import { LoginButton } from "@components/common";
import { useNavigate } from "react-router-dom";

export const LoginInfo = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col justify-end gap-y-[20px]">
      <div className="flex flex-col gap-y-[10px] items-center">
        <LoginButton provider="naver" label="네이버로 계속하기" />
        <LoginButton provider="google" label="구글로 계속하기" />
      </div>

      <div className="flex flex-col gap-y-[10px] text-center">
        <div
          className="btnFont text-main-deep"
          onClick={() => {
            navigate("/s");
          }}
        >
          가게를 운영하고 계신가요?
        </div>
        <div className="flex flex-row justify-center gap-x-[20px] text-[#9D9D9D] tagFont">
          <div onClick={() => navigate("/docs/tos")}>이용약관</div>
          <div onClick={() => navigate("/docs/privacy")}>개인정보처리방침</div>
        </div>
      </div>
    </div>
  );
};
