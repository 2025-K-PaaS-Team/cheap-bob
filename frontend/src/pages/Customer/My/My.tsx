import { CommonModal } from "@components/common";
import { WithdrawCustomer } from "@services";
import { formatErrMsg } from "@utils";
import { useState } from "react";
import { useNavigate } from "react-router";

const My = () => {
  const navigate = useNavigate();
  const [showWarn, setShowWarn] = useState<Boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [modalMsg, setModalMsg] = useState("");

  const handlePostWithdraw = async () => {
    setShowWarn(false);
    try {
      await WithdrawCustomer();
      navigate("withdraw");
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
      return;
    }
  };
  return (
    <div className="px-[20px] w-full">
      {/* order history & nutrition goal */}
      <div className="grid grid-cols-2 gap-x-[10px] pt-[14px] pb-[95px]">
        <div className="flex flex-col bg-[#717171] p-[15px] text-white rounded-[5px] h-[109px]">
          <div
            className="font-semibold text-[15px]"
            onClick={() => navigate("/c/order")}
          >
            주문 내역
          </div>
        </div>
        <div className="flex flex-col bg-[#717171] p-[15px] text-white rounded-[5px] h-[109px]">
          <div className="font-semibold text-[15px]">영양 목표</div>
        </div>
      </div>
      {/* policy */}
      <div className="text-[15px] py-[20px] font-bold">약관 및 정책</div>
      {/* connect to seller */}
      <div
        className="text-[15px] py-[20px] font-bold"
        onClick={() => navigate("/s")}
      >
        사장님으로 접속
      </div>
      {/* logout */}
      <div className="bodyFont font-bold py-[20px] border-b border-black/10">
        <div onClick={() => navigate("/c")}>로그아웃</div>
      </div>
      {/* withdraw */}
      <div
        className="bodyFont font-bold text-sub-red py-[20px]"
        onClick={() => setShowWarn(true)}
      >
        <div>계정 탈퇴</div>
      </div>
      {/* withdraw member */}
      <div className="text-[15px] py-[20px] font-bold">계정탈퇴</div>

      {/* show modal */}
      {showModal && (
        <CommonModal
          desc={modalMsg}
          confirmLabel="확인"
          onConfirmClick={() => setShowModal(false)}
          category="green"
        />
      )}

      {/* show warn modal */}
      {showWarn && (
        <CommonModal
          desc="계정 탈퇴 시, <b>가게 정보는 유지</b>되지만<br/> <b>가게가 더이상 타 사용자에게 노출되지 않습니다.</b> <br/> <br/> 탈퇴하시겠습니까?"
          confirmLabel="네, 탈퇴합니다."
          onConfirmClick={handlePostWithdraw}
          onCancelClick={() => setShowWarn(false)}
          category="red"
          className="text-start"
        />
      )}
    </div>
  );
};

export default My;
