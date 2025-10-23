import { useNavigate } from "react-router-dom";
interface DetailHeaderProps {
  name: string;
}
const DetailHeader = ({ name }: DetailHeaderProps) => {
  const navigate = useNavigate();

  if (!name) {
    return null;
  }

  return (
    <div className="min-h-[60px] mt-[10px] px-[20px] grid grid-cols-3 items-center">
      {/* left */}
      <img
        src="/icon/before.svg"
        alt="beforeArrowIcon"
        onClick={() => navigate(-1)}
      />

      {/* center */}
      <div className="font-bold text-[15px] text-center">{name || ""}</div>

      {/* right */}
      <div />
    </div>
  );
};

export default DetailHeader;
