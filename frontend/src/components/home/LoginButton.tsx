import axios from "axios";

interface loginButtonProps {
  provider: "kakao" | "google" | "naver";
  label: string;
  color: string;
}

const LoginButton = ({ provider, label, color }: loginButtonProps) => {
  const handleLogin = async () => {
    const state = provider === "kakao" ? "1004" : null;
    window.location.href = `${
      import.meta.env.VITE_API_BASE_URL
    }/api/v1/auth/${provider}/login/customer${state ? `?state=${state}` : ""}`;
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
