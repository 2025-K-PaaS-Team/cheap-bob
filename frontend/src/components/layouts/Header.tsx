import { useLocation } from "react-router";

const Header = () => {
  const location = useLocation();
  const path = location.pathname;

  if (path !== "/c/store-list") {
    return null;
  }

  return (
    <div className="p-4 flex flex-row justify-between items-center">
      <div>광화문 홍길동 어쩌구로 행복하동</div>
      {/* icon list */}
      <div className="flex flex-row gap-x-4">
        <img src="/icon/search.svg" alt="searchIcon" width="25" />
        <img src="/icon/notification.svg" alt="searchIcon" width="25" />
      </div>
    </div>
  );
};

export default Header;
