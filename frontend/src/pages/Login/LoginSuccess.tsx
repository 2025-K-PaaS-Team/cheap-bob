const LoginSuccess = () => {
  const token = localStorage.getItem("accessToekn");
  console.log("token", token);
  return (
    <>
      <div>Login Success</div>
    </>
  );
};

export default LoginSuccess;
