import { CommonDesc } from "@components/common";
import { useLocation } from "react-router-dom";
import "swiper/css";

const StoreDetail = () => {
  const location = useLocation();
  const { desc, name } = location.state as { desc: string; name: string };
  return (
    <>
      {/* show desc modal */}
      <CommonDesc desc={desc || ""} name={name || ""} />
    </>
  );
};

export default StoreDetail;
