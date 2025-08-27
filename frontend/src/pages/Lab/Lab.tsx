import { Outlet } from "react-router";
import { useNavigate } from "react-router";

const Lab = () => {
  const navigate = useNavigate();

  return (
    <div className="gap-y-5">
      <h3
        className={`bg-green-400 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => navigate("/lab/map")}
      >
        NAVER MAP API 구경하기
      </h3>
      <h3
        className={`bg-pink-400 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => navigate("/store-list")}
      >
        Store List 페이지 구경하기
      </h3>
      <h3
        className={`bg-yellow-400 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => navigate("/store-detail")}
      >
        Store Detail 페이지 구경하기
      </h3>
      <Outlet />
    </div>
  );
};

export default Lab;
