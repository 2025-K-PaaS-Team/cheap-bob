import { PostLogout } from "@services/common/auth";
import { formatErrMsg } from "@utils";
import { useNavigate } from "react-router-dom";

interface BottomListType {
  setModalMsg: (msg: string) => void;
  setShowModal: (show: boolean) => void;
  setShowWarn: (show: boolean) => void;
}

export const BottomList = ({
  setModalMsg,
  setShowModal,
  setShowWarn,
}: BottomListType) => {
  const navigate = useNavigate();

  const isLocal = import.meta.env.VITE_IS_LOCAL === "true";
  const state = isLocal ? "1004" : undefined;

  const handleLogout = async () => {
    try {
      await PostLogout(state);
      navigate("/c");
    } catch (err) {
      setModalMsg(formatErrMsg(err));
      setShowModal(true);
    }
  };

  return (
    <div className="flex flex-col">
      {/* prefer menu */}
      <div
        onClick={() => navigate("/c/change/menu")}
        className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10"
      >
        <div>선호 메뉴</div>
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>
      {/* prefer topping */}
      <div
        onClick={() => navigate("/c/change/topping")}
        className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10"
      >
        <div>선호 토핑</div>
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>
      {/* allergy */}
      <div
        onClick={() => navigate("/c/change/allergy")}
        className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10"
      >
        <div>못먹는 음식</div>
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>
      {/* order */}
      <div
        onClick={() => navigate("/c/order/all")}
        className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10"
      >
        <div>주문 내역</div>
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>
      {/* policy */}
      <div
        className="bodyFont font-bold py-[20px] flex flex-row justify-between border-b border-black/10"
        onClick={() => navigate("/docs/tos")}
      >
        <div>서비스 이용약관</div>
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>
      {/* logout */}
      <div className="bodyFont font-bold py-[20px] border-b border-black/10">
        <div
          onClick={() => {
            handleLogout();
          }}
        >
          로그아웃
        </div>
      </div>
      {/* withdraw */}
      <div
        className="bodyFont font-bold text-sub-red py-[20px]"
        onClick={() => setShowWarn(true)}
      >
        <div>계정 탈퇴</div>
      </div>
    </div>
  );
};
