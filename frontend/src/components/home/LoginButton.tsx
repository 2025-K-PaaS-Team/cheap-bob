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
    const state = isLocal ? null : "1004";
    window.location.href = `${
      import.meta.env.VITE_API_BASE_URL
    }/api/v1/auth/${provider}/login/${isCustomer ? `customer` : "seller"}${
      state ? `?state=${state}` : ""
    }`;
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
