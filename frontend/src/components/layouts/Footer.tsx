import { useLocation } from "react-router";
import FooterItem from "./FooterItem";

const Footer = () => {
  const location = useLocation();
  const path = location.pathname;

  if (path === "/" || path.includes("login")) {
    return null;
  }

  return (
    <div className="grid grid-cols-4 items-center text-center p-4">
      <FooterItem img={"/icon/search.svg"} label={"홈"} to={"/"} />
      <FooterItem img={"/icon/search.svg"} label={"실험실"} to={"/lab"} />
      <FooterItem
        img={"/icon/search.svg"}
        label={"리스트"}
        to={"/store-list"}
      />
      <FooterItem
        img={"/icon/search.svg"}
        label={"마이페이지"}
        to={"/my"}
      />
    </div>
  );
};

export default Footer;
