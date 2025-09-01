import { Outlet } from "react-router";
import { useNavigate } from "react-router";
// import axios from "axios";

const CustomerLab = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen gap-y-5 flex flex-col justify-center items-center">
      <button
        className={`bg-green-400 p-3 rounded-xl text-center cursor-pointer`}
        onClick={() => navigate("map")}
      >
        NAVER MAP API
      </button>

      <Outlet />
    </div>
  );
};

export default CustomerLab;
