export const SearchBar = ({ onClick }: { onClick: () => void }) => (
  <div className="border border-1 border-main-deep flex flex-row justify-between px-[18px] py-[16px] h-[54px] rounded-[50px]">
    <input
      type="text"
      onClick={onClick}
      className="focus:outline-none w-full"
      placeholder="랜덤팩을 찾으시나요?"
      readOnly
    />
    <img src="/icon/search.svg" alt="searchIcon" />
  </div>
);
