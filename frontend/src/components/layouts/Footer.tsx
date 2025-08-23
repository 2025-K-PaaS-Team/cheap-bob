import { useLocation } from "react-router";

const Footer = () => {
  const location = useLocation();
  const path = location.pathname;

  if (path === "/" || path.includes("login")) {
    return null;
  }

  const FooterItem = (
    <div className="flex flex-col items-center gap-y-1">
      <img src="/rice.svg" alt="rice" width="30" />
      <div className="">Item</div>
    </div>
  );

  return (
    <div className="grid grid-cols-4 items-center text-center p-4">
      {FooterItem}
      {FooterItem}
      {FooterItem}
      {FooterItem}
    </div>
  );
};

export default Footer;
