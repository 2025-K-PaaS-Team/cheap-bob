import { getLayoutByPath } from "@utils";
import { useLocation, useNavigate } from "react-router-dom";

interface HeaderProps {
  swiperRef?: any;
}

const Header = ({ swiperRef }: HeaderProps) => {
  const { pathname } = useLocation();
  const navigate = useNavigate();

  const layout = getLayoutByPath(pathname);

  const handleClickBefore = () => {
    if (layout.key === "Noti") {
      navigate("/c/stores", { replace: true });
    } else if (layout.key === "onBoarding" && swiperRef?.current) {
      const swiper = swiperRef.current;
      if (swiper.activeIndex > 0) {
        swiper.slidePrev();
      } else {
        navigate("/c", { replace: true });
      }
    } else {
      navigate(-1);
    }
  };

  return (
    <>
      <div className="min-h-[60px] mt-[10px] px-[20px] grid grid-cols-3 items-center">
        {/* left */}
        {layout.back ? (
          <img
            src="/icon/before.svg"
            alt="beforeArrowIcon"
            onClick={handleClickBefore}
          />
        ) : layout?.loc ? (
          <div className="flex gap-x-[5px]">
            <img
              src="/icon/location.svg"
              alt="locationIcon"
              onClick={() => navigate("/c/location")}
            />
            <div className="bodyFont font-bold">관악구</div>
          </div>
        ) : (
          <div />
        )}

        {/* center */}
        {layout.title ? (
          <div className="font-bold text-[15px] text-center">
            {layout.title || ""}
          </div>
        ) : layout?.centerIcon ? (
          <div className="flex justify-center">
            <img src="/typo.svg" alt="typoIcon" width="60px" />
          </div>
        ) : (
          <div />
        )}

        {/* right */}
        <div className="flex flex-row justify-end gap-x-[20px]">
          {layout.heart && (
            <img
              src="/icon/heartFull.svg"
              alt="heartIcon"
              onClick={() => navigate("/c/favorite")}
            />
          )}
          {layout.noti && (
            <img
              src="/icon/notification.svg"
              alt="notificationIcon"
              onClick={() => navigate("/c/noti")}
            />
          )}
        </div>
      </div>
    </>
  );
};

export default Header;
