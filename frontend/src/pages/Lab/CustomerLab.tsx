import { Outlet } from "react-router";
import { useNavigate } from "react-router";
import axios from "axios";

const CustomerLab = () => {
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

  return (
    <div className="min-h-screen gap-y-5 flex flex-col justify-center items-center">
      <button
        className={`bg-green-400 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => navigate("/lab/map")}
      >
        NAVER MAP API 구경하기
      </button>
      <button
        className={`bg-pink-400 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => navigate("/store-list")}
      >
        Store List 페이지 구경하기
      </button>
      <button
        className={`bg-yellow-400 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => navigate("/store-detail")}
      >
        Store Detail 페이지 구경하기
      </button>
      <Outlet />
    </div>
  );
};

export default CustomerLab;
