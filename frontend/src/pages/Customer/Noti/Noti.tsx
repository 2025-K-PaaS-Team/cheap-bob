const Noti = () => {
  const isNoti = false;

  if (!isNoti) {
    return (
      <div className="flex flex-col w-full h-full justify-center items-center">
        <img
          src="/icon/saladBowl.svg"
          alt="saladBowlIcon"
          className="pb-[26px] w-[116px]"
        />
        <div className="text-[20px] pb-[17px] font-bold">
          주문내역이 비어있어요.
        </div>
        <div className="text-[12px] font-base">
          다양한 랜덤팩을 주문하고 픽업해보세요.
        </div>
      </div>
    );
  }

  return <></>;
};

export default Noti;
