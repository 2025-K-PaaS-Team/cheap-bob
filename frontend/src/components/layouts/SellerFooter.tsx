import { useLocation } from "react-router";
import FooterItem from "./FooterItem";

const SellerFooter = () => {
  const location = useLocation();
  const path = location.pathname;

  if (path === "/" || path.includes("login")) {
    return null;
  }

  const items = [
    { label: "주문 관리", to: "order", icon: "receipt" },
    { label: "매장 관리", to: "dashboard", icon: "home" },
    { label: "마이페이지", to: "billing", icon: "user" },
  ];

  return (
    <div className="grid grid-cols-3 items-center text-center p-4 border-t border-black/10 bg-white h-[100px]">
      {items.map((item) => {
        const isActive = path.includes(item.to);
        const iconName = `${item.icon}${isActive ? "Full" : ""}.svg`;

        return (
          <FooterItem
            key={item.to}
            label={item.label}
            to={`/s/${item.to}`}
            img={`/icon/${iconName}`}
            className={
              isActive
                ? "text-custom-black font-bold"
                : "text-[#393939] hintFont"
            }
          />
        );
      })}
    </div>
  );
};

export default SellerFooter;
