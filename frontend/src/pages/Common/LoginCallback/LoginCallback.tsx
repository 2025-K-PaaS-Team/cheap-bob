import { GetSellerEmail } from "@services";
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
      const needRegisterProductOnly = status == "product";
      const needSignup = status !== "complete";

      console.log("needRegisterProductOnly", needRegisterProductOnly);

      if (needRegisterProductOnly) {
        await GetSellerEmail();
        navigate("/s/signup/10");
        return;
      }

      if (conflict == "1") {
        navigate("/auth/fail");
      } else {
        if (needSignup) {
          navigate(loginRole == "customer" ? "/c/signup" : "/s/signup/0");
        } else {
          navigate(loginRole == "customer" ? "/c/stores" : "/s/dashboard");
        }
      }
    } catch (err: unknown) {
      console.warn(err);
    }
  };

  useEffect(() => {
    handleCheckConflict();
  }, [searchParams, navigate]);

  return null;
};

export default LoginCallback;
