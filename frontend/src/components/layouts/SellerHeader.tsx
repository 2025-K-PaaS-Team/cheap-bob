import { getSellerLayoutByPath } from "@utils";
import { useLocation, useNavigate } from "react-router-dom";

const SellerHeader = () => {
  const { pathname } = useLocation();
  const layout = getSellerLayoutByPath(pathname);
  const navigate = useNavigate();

  return (
    <>
      <div className="h-[75px] pt-[15px] px-[20px] grid grid-cols-3 items-center">
        {/* left */}
        {layout.back && (
          <img
            src="/icon/before.svg"
            alt="beforeArrowIcon"
            onClick={() => navigate(-1)}
          />
        )}

        {/* center */}
        <div className="font-bold text-[15px] text-center text-nowrap">
          {layout.title}
        </div>
      </div>
    </>
  );
};

export default SellerHeader;
