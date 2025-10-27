import type { UserRoleType } from "@interface";
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
      const isCompleteUser = status == "complete";
      const loginRole = sessionStorage.getItem("loginRole");

      if (conflict == "1") {
        navigate("/auth/fail");
      } else {
        if (isCompleteUser && userInfo) {
          // customer complete
          if (loginRole === "customer") {
            navigate("/c");
          }
          // seller complete
          else if (loginRole === "seller") {
            navigate("/s");
          }
          // finally
          sessionStorage.removeItem("loginRole");
        }
        // need to signup
        else {
          if (status === "profile") navigate("/c/signup");
          if (status === "store") navigate("/s/signup/0");
          if (status === "product") navigate("/s/signup/10");
        }
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
