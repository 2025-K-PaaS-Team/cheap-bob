import { useNavigate } from "react-router";

const Header = () => {
  const navigate = useNavigate();
  const handleClickBefore = () => {
    navigate(-1);
  };

  return (
    <>
      <div className="h-[85px] pt-[40px] px-[14px]">
        <img
          src="/icon/before.svg"
          alt="beforeArrow"
          onClick={handleClickBefore}
        />
      </div>
    </>
  );
};

export default Header;
