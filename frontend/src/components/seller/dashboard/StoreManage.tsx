import { useNavigate } from "react-router";

const StoreManage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-y-[11px] mx-[20px]">
      {/* 나의 매장 */}
      <div className="flex flex-row text-bold justify-between h-[59px] items-center">
        <div className="font-bold">나의 매장</div>
        <div
          className="text-black/80"
          onClick={() => navigate("/s/change/store")}
        >
          매장 정보 변경 &gt;
        </div>
      </div>
      {/* 운영 시간 */}
      <div className="flex flex-row text-bold justify-between h-[59px] items-center">
        <div className="font-bold">운영 시간</div>
        <div
          className="text-black/80"
          onClick={() => navigate("/s/change/operation")}
        >
          운영 정보 변경 &gt;
        </div>
      </div>
      {/* 판매 패키지 */}
      <div className="flex flex-row text-bold justify-between h-[59px] items-center">
        <div className="font-bold">판매 패키지</div>
        <div
          className="text-black/80"
          onClick={() => navigate("/s/change/package")}
        >
          패키지 정보 변경 &gt;
        </div>
      </div>
    </div>
  );
};

export default StoreManage;
