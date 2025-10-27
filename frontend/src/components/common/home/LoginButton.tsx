import type { UserRoleType } from "@interface";
import { GetUserRole } from "@services/common/auth";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface loginButtonProps {
  provider: "kakao" | "google" | "naver";
  label: string;
  isCustomer?: boolean;
}

const LoginButton = ({
  provider,
  label,
  isCustomer = true,
}: loginButtonProps) => {
  // customer style
  const providerStyleMap: Record<string, string> = {
    kakao: "bg-[#FEE500] text-custom-black",
    naver: "bg-[#03C75A] text-white",
    google: "bg-[#EFEFEF] text-custom-black",
  };
  const navigate = useNavigate();
  const providerStyle = providerStyleMap[provider];
  const [userInfo, setUserInfo] = useState<UserRoleType | null>(null);

  const handleCheckWithdraw = () => {
    if (
      userInfo?.email &&
      userInfo?.user_type == `${isCustomer ? "customer" : "seller"}` &&
      userInfo?.status === "complete" &&
      !userInfo?.is_active
    ) {
      navigate("/withdraw/cancel");
      return true;
    }
    return false;
  };

  // handle click login btn
  const handleClickLogin = () => {
    const isWithdraw = handleCheckWithdraw();
    if (isWithdraw) return;

    const isLocal = import.meta.env.VITE_IS_LOCAL === "true";
    const state = isLocal ? "1004" : undefined;
    const baseUrl = `${
      import.meta.env.VITE_API_BASE_URL
    }/api/v1/auth/${provider}/login/${isCustomer ? `customer` : "seller"}`;

    sessionStorage.setItem("loginRole", isCustomer ? "customer" : "seller");

    const url = state ? `${baseUrl}?state=${state}` : baseUrl;
    window.location.href = url;
  };

  useEffect(() => {
    const init = async () => {
      try {
        const res = await GetUserRole();
        setUserInfo(res);
      } catch (err) {}
    };

    init();
  }, []);

  return (
    <div
      className={`flex w-[350px] h-[54px] items-center ${providerStyle} px-[24px] rounded-xl text-center font-bold`}
      onClick={handleClickLogin}
    >
      <img src={`/icon/${provider}.svg`} alt={provider} />
      <div className="text-center w-full mr-[28px]">{label}</div>
    </div>
  );
};

export default LoginButton;
