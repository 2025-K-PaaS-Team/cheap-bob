import { sellerLayoutMap } from "@constant";
import type { SellerLayoutType } from "@interface";
import { useNavigate } from "react-router-dom";

interface HeaderProps {
  layout: SellerLayoutType;
}

const SellerHeader = ({ layout }: HeaderProps) => {
  const navigate = useNavigate();
  const handleClickBefore = () => {
    navigate(-1);
  };

  const myLayout = sellerLayoutMap[layout];

  return (
    <>
      <div className="h-[75px] pt-[15px] px-[20px] grid grid-cols-3 items-center">
        {/* left */}
        {myLayout.back && (
          <img
            src="/icon/before.svg"
            alt="beforeArrowIcon"
            onClick={handleClickBefore}
          />
        )}

        {/* center */}
        <div className="font-bold text-[15px] text-center text-nowrap">
          {myLayout.title}
        </div>
      </div>
    </>
  );
};

export default SellerHeader;
