import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";

const LoginCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const loginRole = localStorage.getItem("loginRole");

  const handleCheckConflict = async () => {
    try {
      const conflict = searchParams.get("conflict");
      if (conflict == "1") {
        navigate("/auth/fail");
      } else {
        navigate(loginRole == "customer" ? "/c/stores" : "/s/dashboard");
      }
    } catch (err: unknown) {
      console.warn(err);
    }
  };

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      localStorage.setItem("accessToken", token);
      handleCheckConflict();
    } else {
      navigate("/auth/success");
    }
  }, [searchParams, navigate]);

  return null;
};

export default LoginCallback;
