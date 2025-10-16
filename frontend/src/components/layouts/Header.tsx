import { layoutMap } from "@constant";
import type { LayoutType } from "@interface";
import { useNavigate } from "react-router";

interface HeaderProps {
  layout: LayoutType;
}

const Header = ({ layout }: HeaderProps) => {
  const navigate = useNavigate();
  const handleClickBefore = () => {
    navigate(-1);
  };

  const myLayout = layoutMap[layout];

  return (
    <>
      <div className="h-[85px] pt-[15px] px-[20px] grid grid-cols-3 items-center">
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
        <div className="font-bold text-[15px] text-center">
          {myLayout.title}
        </div>

        {/* right */}
        <div className="flex flex-row justify-end gap-x-[20px]">
          {myLayout.heart && (
            <img
              src="/icon/heart.svg"
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
      {/* search bar */}
      {myLayout.search && (
        <div className="border border-1 border-[#222222] flex flex-row justify-between p-[14px] rounded-[58px] m-[20px]">
          <input
            type="text"
            className="focus:outline-none"
            placeholder={myLayout.searchPlaceholder}
          />

          <img src="/icon/search.svg" alt="searchIcon" />
        </div>
      )}
    </>
  );
};

export default Header;
