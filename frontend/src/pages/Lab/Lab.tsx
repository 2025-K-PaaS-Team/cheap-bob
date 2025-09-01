import { Outlet } from "react-router";
import { useNavigate } from "react-router";
import axios from "axios";

const Lab = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("accessToken");

  // api/v1/test/
  // axios
  //   .get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/test/auth`, {
  //     headers: {
  //       Authorization: `Bearer ${token}`,
  //     },
  //   })
  //   .then((res) => {
  //     console.log(res.data);
  //   })
  //   .catch((err) => {
  //     console.error(err);
  //   });

  // 

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
