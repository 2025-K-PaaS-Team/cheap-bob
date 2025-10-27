import { CommonBtn } from "@components/common";
import type { UserRoleType } from "@interface";
import { GetUserRole } from "@services/common/auth";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Lottie from "lottie-react";
import information from "@assets/information.json";

const RoleCheck = () => {
  const navigate = useNavigate();
  const [userInfo, setUserInfo] = useState<UserRoleType | null>(null);

  useEffect(() => {
    const init = async () => {
      const res = await GetUserRole();
      setUserInfo(res);
    };

    init();
  }, []);

  return (
    <div className="flex flex-col flex-1 items-center justify-center text-center mx-auto w-[calc(100%-40px)] gap-y-[20px]">
      <Lottie
        animationData={information}
        style={{ width: "150px", height: "150px" }}
      />
      <div className="titleFont font-bold">확인해주세요</div>
      <div className="bodyFont px-10">
        <b>{userInfo?.user_type === "customer" ? "고객" : "점주"}</b>
        계정으로 <br />
        로그인되어 있는 것 같아요.
        <br />
        {userInfo?.user_type === "customer" ? "고객" : "점주"} 페이지로
        이동하시겠어요?
      </div>

      <div className="flex flex-col w-full gap-y-[10px]">
        <CommonBtn
          label="고객 페이지로 이동하기"
          onClick={() => navigate("/c")}
          notBottom
        />
        <CommonBtn
          label="점주 페이지로 이동하기"
          onClick={() => navigate("/s")}
          notBottom
        />
      </div>
    </div>
  );
};

export default RoleCheck;
