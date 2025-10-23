import { CommonBtn, CommonModal } from "@components/common";
import { PostLogout } from "@services/common/auth";
import { formatErrMsg } from "@utils";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Withdraw = () => {
  const navigate = useNavigate();
  const loginRole = localStorage.getItem("loginRole");
  const isLocal = import.meta.env.VITE_IS_LOCAL === "true";
  const state = isLocal ? "1004" : undefined;
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handleLogout = async () => {
    try {
      await PostLogout(state);
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  return (
    <div className="m-[20px] flex flex-col h-full items-center justify-center text-center text-custom-black">
      <div className="flex flex-col flex-1 items-center justify-center gap-y-[10px]">
        <div className="titleFont">계정 탈퇴가 접수되었습니다.</div>
        <div className="bodyFont">
          지금까지 서비스를 이용해주셔서 감사합니다.
        </div>
      </div>

      <CommonBtn
        label="첫 화면으로"
        onClick={() => {
          localStorage.removeItem("loginRole");
          handleLogout();
          loginRole === "customer" ? navigate("/c") : navigate("/s");
        }}
        category="white"
        notBottom
      />
      <div className="w-full bg-[#e7e7e7] rounded hintFont py-[20px] px-[8px] mt-[10px]">
        탈퇴 처리까지는 최대 1일까지 소요될 수 있습니다.
        <br />
        문의사항: cheapbob2025@gmail.com
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

export default Withdraw;
