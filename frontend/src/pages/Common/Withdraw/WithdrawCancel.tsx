import { CommonBtn, CommonModal } from "@components/common";
import type { UserRoleType } from "@interface";
import { CancelWithdrawCustomer, CancelWithdrawSeller } from "@services";
import { GetUserRole } from "@services/common/auth";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const WithdrawCancel = () => {
  const navigate = useNavigate();
  const isLocal = import.meta.env.VITE_IS_LOCAL === "true";
  const state = isLocal ? "1004" : undefined;

  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [userInfo, setUserInfo] = useState<UserRoleType | null>(null);

  const handleCancelWithdraw = async () => {
    if (userInfo?.user_type == "seller" && userInfo.email) {
      try {
        await CancelWithdrawSeller(state);
        navigate("/s");
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      }
    } else if (userInfo?.user_type == "customer" && userInfo.email) {
      try {
        await CancelWithdrawCustomer(state);
        navigate("/c");
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
            if (userInfo?.user_type === "customer") {
              navigate("/c");
            } else if (userInfo?.user_type === "seller") {
              navigate("/s");
            } else {
              navigate("/");
            }
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
