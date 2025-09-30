import { useNavigate } from "react-router";

interface FooterItemProps {
  label: string;
  img?: string;
  to: string;
  className?: string;
}

const FooterItem = ({ label, img, to, className }: FooterItemProps) => {
  const navigate = useNavigate();

  return (
    <div
      className={`flex flex-col items-center gap-y-1 cursor-pointer ${
        className || ""
      }`}
      onClick={() => navigate(to)}
    >
      {img && <img src={img} alt={label} width="30" />}
      {label}
    </div>
  );
};

export default FooterItem;
