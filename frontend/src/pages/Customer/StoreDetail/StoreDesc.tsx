import { CommonDesc } from "@components/common";
import { useLocation } from "react-router-dom";
import "swiper/css";

const StoreDetail = () => {
  const location = useLocation();
  const desc = location.state as string;

  return (
    <>
      {/* show desc modal */}
      <CommonDesc desc={desc} />
    </>
  );
};

export default StoreDetail;
