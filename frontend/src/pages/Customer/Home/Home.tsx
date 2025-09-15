import { LoginButton } from "@components/home";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import Swiper from "swiper";

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    // if (token) {
    //   navigate("stores");
    // }
  }, []);

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
        <h3
          className="bg-pink-300 p-3 rounded-xl text-center cursor-pointer"
          onClick={() => navigate("/s", { replace: true })}
        >
          점주 페이지로 이동
        </h3>
        <h3
          className="bg-gray-300 p-3 rounded-xl text-center cursor-pointer"
          onClick={() => navigate("/c/lab")}
        >
          실험실로 이동
        </h3>
      </div>
    </div>
  );
};

export default Home;
