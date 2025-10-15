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
    // kakao: "bg-[#FEE500] text-custom-black",
    kakao: "bg-main-500 text-custom-black",
    naver: "bg-[#03C75A] text-white",
    google: "bg-[#EFEFEF] text-custom-black",
  };
  const providerStyle = providerStyleMap[provider];

  // handle click login btn
  const handleClickLogin = () => {
    const isLocal = import.meta.env.VITE_IS_LOCAL === "true";
    const state = isLocal ? "1004" : undefined;

    localStorage.setItem("loginRole", isCustomer ? "customer" : "seller");

    const baseUrl = `${
      import.meta.env.VITE_API_BASE_URL
    }/api/v1/auth/${provider}/login/${isCustomer ? `customer` : "seller"}`;
    const url = state ? `${baseUrl}?state=${state}` : baseUrl;
    window.location.href = url;
  };

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
