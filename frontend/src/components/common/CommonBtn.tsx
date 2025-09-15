type BtnProps = {
  label: string;
};
const CommonBtn = ({ label }: BtnProps) => {
  const handleClickNext = () => {};

  return (
    <button
      onClick={handleClickNext}
      className="absolute bottom-[38px] left-1/2 -translate-x-1/2 font-bold rounded-[10px] text-base border border-[1px] border-[#222222] bg-white w-[350px] h-[54px] flex justify-center items-center"
    >
      {label}
    </button>
  );
};

export default CommonBtn;
