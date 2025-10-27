import type { UserRoleType } from "@interface";
import { GetSellerEmail } from "@services";
import { GetUserRole } from "@services/common/auth";
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

const LoginCallback = () => {
  const [searchParams] = useSearchParams();
  const [userInfo, setuserInfo] = useState<UserRoleType | null>(null);
  const navigate = useNavigate();

  const handleCheckConflict = async () => {
    try {
      const conflict = searchParams.get("conflict");
      const status = searchParams.get("status");
      const needRegisterProductOnly = status == "product";
      const needSignup = status !== "complete";

      if (needRegisterProductOnly) {
        await GetSellerEmail();
        navigate("/s/signup/10");
        return;
      }

      if (conflict == "1") {
        navigate("/auth/fail");
      } else {
        // if (needSignup) {
        //   navigate(loginRole == "customer" ? "/c/signup" : "/s/signup/0");
        // } else {
        //   navigate(loginRole == "customer" ? "/c/stores" : "/s/dashboard");
        // }
      }
    } catch (err: unknown) {
      console.warn(err);
    }
  };

  useEffect(() => {
    const init = async () => {
      const res = await GetUserRole();
      setuserInfo(res);
      handleCheckConflict();
    };
    init();
  }, [searchParams, navigate]);

  return null;
};

export default LoginCallback;
