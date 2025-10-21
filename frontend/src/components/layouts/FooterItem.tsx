import { useNavigate } from "react-router-dom";

interface FooterItemProps {
  label: string;
  img?: string;
  to: string;
  className?: string;
  active?: boolean;
}

const FooterItem = ({ label, img, to, className, active }: FooterItemProps) => {
  const navigate = useNavigate();

  return (
    <div
      className={`flex flex-col items-center gap-y-1 cursor-pointer ${
        active ? "text-custom-black font-bold" : "text-[#393939] hintFont"
      } ${className || ""}`}
      onClick={() => navigate(to)}
    >
      {img && <img src={img} alt={label} width="30" />}
      {label}
    </div>
  );
};

export default FooterItem;
