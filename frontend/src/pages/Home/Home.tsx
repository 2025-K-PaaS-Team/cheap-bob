import { LoginButton } from "@components/home";
import axios from "axios";
import { useEffect } from "react";
import { useNavigate } from "react-router";

const Home = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("accessToken");

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    if (token) {
      navigate("store-list");
    }
  });

  // login localstorage api connection test
  // axios
  //   .get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/test/auth`, {
  //     headers: {
  //       Authorization: `Bearer ${token}`,
  //     },
  //   })
  //   .then((res) => {
  //     console.log(res.data);
  //   })
  //   .catch((err) => {
  //     console.error(err);
  //   });

  return (
    <div className="flex justify-center">
      {/* title */}
      <h1 className="flex">저렴한끼</h1>

      <div className="fixed bottom-30 w-full flex flex-col max-w-[400px]">
        <LoginButton
          provider="kakao"
          label="카카오톡으로 로그인하기"
          color="bg-yellow-500"
        />
        <LoginButton
          provider="naver"
          label="네이버로 로그인하기"
          color="bg-green-500"
        />
        <LoginButton
          provider="google"
          label="구글로 로그인하기"
          color="bg-blue-300"
        />
        <h3
          className="bg-gray-300 p-3 rounded-xl text-center cursor-pointer"
          onClick={() => navigate("/store-list")}
        >
          로그인 스킵
        </h3>
      </div>
    </div>
  );
};

export default Home;
