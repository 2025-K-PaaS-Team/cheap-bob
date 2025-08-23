import { useLocation } from "react-router";

const Header = () => {
  const location = useLocation();
  const path = location.pathname;

  if (path !== "/store-list") {
    return null;
  }

  return (
    <div className="p-4 flex flex-row justify-between">
      <h3 className="border-2 py-2 px-10 w-full">SearchBar & Icon Header</h3>
      <img src="/rice.svg" alt="searchIcon" width="35" />
    </div>
  );
};

export default Header;
