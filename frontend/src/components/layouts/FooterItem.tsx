import { useNavigate } from "react-router";

interface FooterItemProps {
  label: string;
  img: string;
  to: string;
}

const FooterItem = ({ label, img, to }: FooterItemProps) => {
  const navigate = useNavigate();

  return (
    <div
      className="flex flex-col items-center gap-y-1"
      onClick={() => navigate(to)}
    >
      <img src={img} alt={label} width="30" />
      {label}
    </div>
  );
};

export default FooterItem;
