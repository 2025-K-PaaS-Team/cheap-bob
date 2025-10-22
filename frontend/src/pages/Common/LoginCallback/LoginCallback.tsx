import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

const LoginCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const loginRole = localStorage.getItem("loginRole");

  const handleCheckConflict = async () => {
    try {
      const conflict = searchParams.get("conflict");
      const status = searchParams.get("status");
      const needSignup = status !== "complete";

      if (conflict == "1") {
        navigate("/auth/fail");
      } else {
        if (needSignup) {
          navigate(loginRole == "customer" ? "/c/signup" : "/s/signup");
        } else {
          navigate(loginRole == "customer" ? "/c/stores" : "/s/dashboard");
        }
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
      console.warn("No token found in query");
      navigate("/auth/fail");
    }
  }, [searchParams, navigate]);

  return null;
};

export default LoginCallback;
