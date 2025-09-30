import { useLocation } from "react-router";
import FooterItem from "./FooterItem";

const SellerFooter = () => {
  const location = useLocation();
  const path = location.pathname;

  if (path === "/" || path.includes("login")) {
    return null;
  }

  const items = [
    { label: "주문 관리", to: "order" },
    { label: "매장 관리", to: "dashboard" },
    { label: "정산 관리", to: "billing" },
  ];

  return (
    <div className="grid grid-cols-3 items-center text-center p-4 bg-[#D9D9D9] h-[68px]">
      {items.map((item) => (
        <FooterItem
          key={item.to}
          label={item.label}
          to={item.to}
          className={path.includes(item.to) ? "font-bold" : "font-normal"}
        />
      ))}
    </div>
  );
};

export default SellerFooter;
