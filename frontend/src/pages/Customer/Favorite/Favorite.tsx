const Favorite = () => {
  const isFav = false;

  if (!isFav) {
    return (
      <div className="flex flex-col w-full h-full justify-center items-center">
        <img
          src="/icon/saladBowl.svg"
          alt="saladBowlIcon"
          className="pb-[26px] w-[116px]"
        />
        <div className="text-[20px] pb-[17px] font-bold">
          아직 관심 가게가 없어요.
        </div>
        <div className="text-[12px] font-base">
          다양한 가게를 확인하고 주문해보세요.
        </div>
      </div>
    );
  }

  return <></>;
};

export default Favorite;
