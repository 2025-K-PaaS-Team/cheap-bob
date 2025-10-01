import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";

const LoginCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const handleCheckConflict = async () => {
    try {
      const conflict = searchParams.get("conflict");
      alert(conflict);
      if (conflict == "1") {
        navigate("/auth/fail");
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
