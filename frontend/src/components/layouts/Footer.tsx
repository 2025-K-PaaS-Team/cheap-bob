import { useLocation } from "react-router";
import FooterItem from "./FooterItem";

const Footer = () => {
  const location = useLocation();
  const path = location.pathname;

  if (path === "/" || path.includes("login")) {
    return null;
  }

  return (
    <div className="grid grid-cols-3 items-center text-center p-4 border-t border-black/10">
      <FooterItem
        label="홈"
        to="/c/stores"
        img={path === "/c/stores" ? "/icon/homeFull.svg" : "/icon/home.svg"}
        active={path === "/c/stores"}
      />
      <FooterItem
        label="주문현황"
        to="/c/order"
        img={
          path === "/c/order" ? "/icon/receiptFull.svg" : "/icon/receipt.svg"
        }
        active={path === "/c/order"}
      />
      <FooterItem
        label="마이페이지"
        to="/c/my"
        img={path === "/c/my" ? "/icon/userFull.svg" : "/icon/user.svg"}
        active={path === "/c/my"}
      />
    </div>
  );
};

export default Footer;
