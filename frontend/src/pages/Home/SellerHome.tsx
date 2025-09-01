import { LoginButton } from "@components/home";
import { useEffect } from "react";
import { useNavigate } from "react-router";

const SellerHome = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    if (token) {
      alert(
        "기존 로그인 기록이 감지되었습니다.\n 3초 뒤 점주용 실험실 페이지로 이동합니다."
      );
      setTimeout(() => {
        navigate("lab");
      }, 3000);
    }
  });

  return (
    <div className="flex justify-center">
      {/* title */}
      <h1 className="flex">저렴한끼</h1>

      <div className="fixed bottom-30 w-full flex flex-col max-w-[400px]">
        <LoginButton
          provider="kakao"
          label="[점주] 카카오톡으로 로그인하기"
          color="bg-amber-500"
          isCustomer={false}
        />
        <LoginButton
          provider="naver"
          label="[점주] 네이버로 로그인하기"
          color="bg-teal-500"
          isCustomer={false}
        />
        <h3
          className="bg-gray-300 p-3 rounded-xl text-center cursor-pointer"
          onClick={() => navigate("/lab")}
        >
          로그인 스킵하고 페이지 탐험하기
        </h3>
      </div>
    </div>
  );
};

export default SellerHome;
