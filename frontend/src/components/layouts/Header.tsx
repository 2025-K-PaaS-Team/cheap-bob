import { layoutMap } from "@constant";
import type { LayoutType } from "@interface";
import { useNavigate } from "react-router";

interface HeaderProps {
  layout: LayoutType;
  swiperRef: React.RefObject<any>;
}

const Header = ({ layout, swiperRef }: HeaderProps) => {
  const navigate = useNavigate();
  const handleClickBefore = () => {
    if (layout === "onBoarding" && swiperRef?.current) {
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

  const myLayout = layoutMap[layout];

  return (
    <>
      <div className="min-h-[60px] mt-[10px] px-[20px] grid grid-cols-3 items-center">
        {/* left */}
        {myLayout.back ? (
          <img
            src="/icon/before.svg"
            alt="beforeArrowIcon"
            onClick={handleClickBefore}
          />
        ) : myLayout.loc ? (
          <img
            src="/icon/location.svg"
            alt="locationIcon"
            onClick={() => navigate("/c/location")}
          />
        ) : (
          <div />
        )}

        {/* center */}
        {myLayout.title ? (
          <div className="font-bold text-[15px] text-center">
            {myLayout.title}
          </div>
        ) : myLayout?.centerIcon ? (
          <div className="flex justify-center">
            <img src="/icon/angrySalad.svg" alt="angrySaladIcon" width="47px" />
          </div>
        ) : (
          <div />
        )}

        {/* right */}
        <div className="flex flex-row justify-end gap-x-[20px]">
          {myLayout.heart && (
            <img
              src="/icon/heartFull.svg"
              alt="heartIcon"
              onClick={() => navigate("/c/favorite")}
            />
          )}
          {myLayout.noti && (
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
