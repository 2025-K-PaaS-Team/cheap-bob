import { CommonBtn, CommonModal } from "@components/common";
import {
  CancelWithdrawCustomer,
  CancelWithdrawSeller,
  GetCustomerEmail,
  GetSellerEmail,
} from "@services";
import { formatErrMsg } from "@utils";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";

const WithdrawCancel = () => {
  const navigate = useNavigate();
  const loginRole = localStorage.getItem("loginRole");
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");
  const [email, setEmail] = useState<string>("");

  const handleCancelWithdraw = async () => {
    if (loginRole === "seller") {
      try {
        await CancelWithdrawSeller();
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      }
    } else {
      try {
        await CancelWithdrawCustomer();
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      }
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        if (loginRole === "seller") {
          const res = await GetSellerEmail();
          setEmail(res.email);
        } else {
          const res = await GetCustomerEmail();
          setEmail(res.email);
        }
      } catch (err) {
        setModalMsg(formatErrMsg(err));
        setShowModal(true);
      }
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
      <div className="bodyFont mb-[150px]">{email}</div>

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
            loginRole === "seller" ? navigate("/s") : navigate("/c");
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
