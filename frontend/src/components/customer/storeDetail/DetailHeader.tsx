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
    <div className="min-h-[60px] mt-[10px] px-[20px] flex flex-row items-center">
      {/* left */}
      <div className="w-5">
        <img
          src="/icon/before.svg"
          alt="beforeArrowIcon"
          onClick={() => navigate(-1)}
        />
      </div>

      {/* center */}
      <div className="font-bold text-[15px] text-center w-full pr-5">
        {name || ""}
      </div>
    </div>
  );
};

export default DetailHeader;
