import { CommonBtn, CommonModal } from "@components/common";
import type { UserRoleType } from "@interface";
import { CancelWithdrawCustomer, CancelWithdrawSeller } from "@services";
import { GetUserRole, PostLogout } from "@services/common/auth";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Lottie from "lottie-react";
import information from "@assets/information.json";

const WithdrawCancel = () => {
  const navigate = useNavigate();
  const isLocal = import.meta.env.VITE_IS_LOCAL === "true";
  const state = isLocal ? "1004" : undefined;

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [userInfo, setUserInfo] = useState<UserRoleType | null>(null);

  const handleLogout = async () => {
    try {
      await PostLogout(state);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  const handleCancelWithdraw = async () => {
    if (userInfo?.user_type == "seller" && userInfo.email) {
      try {
        await CancelWithdrawSeller();
        handleLogout();
        navigate("/s/dashboard");
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      }
    } else if (userInfo?.user_type == "customer" && userInfo.email) {
      try {
        await CancelWithdrawCustomer();
        handleLogout();
        navigate("/c/stores");
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      }
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        const res = await GetUserRole();
        setUserInfo(res);
      } catch (err) {}
    };
    init();
  }, []);

  if (!userInfo) {
    return (
      <div className="flex flex-col flex-1 items-center justify-center text-center mx-auto w-[calc(100%-40px)] gap-y-[20px]">
        <Lottie
          animationData={information}
          style={{ width: "150px", height: "150px" }}
        />
        <div className="titleFont font-bold">404</div>
        <div className="text-[16px]">탈퇴 기록이 없거나 존재하지 않습니다.</div>

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
  }

  return (
    <div className="relative mx-[20px] flex flex-col h-full items-start justify-center text-center text-custom-black">
      <div className="w-full text-start titleFont pb-[65px]">
        해당 계정은 <br />
        탈퇴 작업이 진행중입니다. <br />
        <br />
        탈퇴를 취소하겠습니까?
      </div>
      {/* need to fix */}
      {/* email */}
      <div className="bodyFont mb-[150px]">{userInfo?.email}</div>

      {/* notice */}
      <div className="absolute bottom-25 hintFont text-center w-full">
        회원 탈퇴 작업이 끝나기 전까진 재가입이 불가능해요.
      </div>

      {/* btn */}
      <div className="absolute bottom-5 w-full gap-x-[11px] grid grid-cols-3">
        <CommonBtn
          label="아니오"
          notBottom
          category="grey"
          className="w-full"
          onClick={() => {
            handleLogout();
          }}
        />
        <CommonBtn
          label="탈퇴 취소하기"
          notBottom
          className="w-full col-span-2"
          onClick={handleCancelWithdraw}
        />
      </div>

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}
    </div>
  );
};

export default WithdrawCancel;
