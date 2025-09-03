interface loginButtonProps {
  provider: "kakao" | "google" | "naver";
  label: string;
  color: string;
  isCustomer?: boolean;
}

const LoginButton = ({
  provider,
  label,
  color,
  isCustomer = true,
}: loginButtonProps) => {
  const handleLogin = () => {
    const isLocal = import.meta.env.VITE_IS_LOCAL === "true";
    const state = isLocal ? "1004" : null;
    const baseUrl = `${
      import.meta.env.VITE_API_BASE_URL
    }/api/v1/auth/${provider}/login/${isCustomer ? `customer` : "seller"}`;
    const url = state ? `${baseUrl}?state=${state}` : baseUrl;
    window.location.href = url;
  };

  return (
    <h3
      className={`${color} p-3 rounded-xl text-center cursor-pointer`}
      onClick={handleLogin}
    >
      {label}
    </h3>
  );
};

export default LoginButton;
