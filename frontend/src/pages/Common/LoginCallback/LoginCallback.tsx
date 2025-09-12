import { CheckCustomerDetail } from "@services";
import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";

const LoginCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const handleCheckCustomerDetail = async () => {
    try {
      const res = await CheckCustomerDetail();

      if (res.has_detail) {
        navigate("/");
      } else {
        // navigate("/c/signup");
      }
    } catch (err: unknown) {
      console.error("err", err);
    }
  };

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      localStorage.setItem("accessToken", token);
      handleCheckCustomerDetail();
    } else {
      navigate("/auth/success");
    }
  }, [searchParams, navigate]);

  return null;
};

export default LoginCallback;
