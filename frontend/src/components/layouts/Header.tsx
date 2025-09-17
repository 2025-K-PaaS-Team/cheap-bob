import { useNavigate } from "react-router";

interface HeaderProps {
  title?: string;
}

const Header = ({ title }: HeaderProps) => {
  const navigate = useNavigate();
  const handleClickBefore = () => {
    navigate(-1);
  };

  const backType = false;

  return (
    <>
      <div className="h-[85px] pt-[40px] px-[20px] grid grid-cols-3 items-center">
        {backType ? (
          <img
            src="/icon/before.svg"
            alt="beforeArrowIcon"
            onClick={handleClickBefore}
          />
        ) : (
          <img src="/icon/location.svg" alt="locationIcon" />
        )}

        <div className="font-bold text-[15px] text-center">{title}</div>
        <div className="flex flex-row justify-end gap-x-[20px]">
          <img src="/icon/heart.svg" alt="heartIcon" />
          <img src="/icon/notification.svg" alt="notificationIcon" />
        </div>
      </div>
      <div className="border border-1 border-[#222222] flex flex-row justify-between p-[14px] rounded-[58px] m-[20px]">
        <input
          type="text"
          className="focus:outline-none"
          placeholder="랜덤팩을 찾으시나요?"
        />

        <img src="/icon/search.svg" alt="searchIcon" />
      </div>
    </>
  );
};

export default Header;
