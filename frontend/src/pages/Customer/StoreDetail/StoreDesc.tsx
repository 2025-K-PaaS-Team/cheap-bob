import { CommonDesc } from "@components/common";
import { useLocation } from "react-router-dom";
import "swiper/css";

const StoreDetail = () => {
  const location = useLocation();
  const { desc, name, phone } = location.state as {
    desc: string;
    name: string;
    phone: string;
  };
  return (
    <>
      {/* show desc modal */}
      <CommonDesc desc={desc || ""} name={name || ""} phone={phone || ""} />
    </>
  );
};

export default StoreDetail;
