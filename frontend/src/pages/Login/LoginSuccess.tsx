import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";

const LoginSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      localStorage.setItem("accessToken", token);

      navigate("/");
    } else {
      navigate("/auth/success");
    }
  }, [searchParams, navigate]);

  return (
    <>
      <div>Login Success</div>
    </>
  );
};

export default LoginSuccess;
