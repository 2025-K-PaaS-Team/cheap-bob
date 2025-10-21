import { useNavigate } from "react-router-dom";

const StoreManage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-y-[11px] mx-[20px] bodyFont font-bold">
      {/* 나의 매장 */}
      <div
        onClick={() => navigate("/s/change/store")}
        className="flex flex-row justify-between h-[60px] items-center border-b-1 border-black/10"
      >
        매장 정보 변경
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>

      {/* 운영 시간 */}
      <div
        onClick={() => navigate("/s/change/operation")}
        className="flex flex-row justify-between h-[60px] items-center border-b-1 border-black/10"
      >
        운영 정보 변경
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>

      {/* 판매 패키지 */}
      <div
        onClick={() => navigate("/s/change/package")}
        className="flex flex-row justify-between h-[60px] items-center border-b-1 border-black/10"
      >
        패키지 정보 변경
        <img src="/icon/next.svg" alt="nextIcon" />
      </div>
    </div>
  );
};

export default StoreManage;
