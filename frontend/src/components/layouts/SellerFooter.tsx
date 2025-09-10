import { useLocation } from "react-router";
import FooterItem from "./FooterItem";

const SellerFooter = () => {
  const location = useLocation();
  const path = location.pathname;

  if (path === "/" || path.includes("login")) {
    return null;
  }

  return (
    <div className="grid grid-cols-4 items-center text-center p-4">
      <FooterItem img={"/icon/search.svg"} label={"홈"} to={"/"} />
      <FooterItem img={"/icon/search.svg"} label={"주문 관리"} to={"order"} />
      <FooterItem img={"/icon/search.svg"} label={"매장 관리"} to={"store"} />
      <FooterItem img={"/icon/search.svg"} label={"실험실"} to={"lab"} />
    </div>
  );
};

export default SellerFooter;
