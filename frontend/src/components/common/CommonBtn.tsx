type BtnProps = {
  label: string;
  onClick: () => void;
};

const CommonBtn = ({ label, onClick }: BtnProps) => {
  return (
    <button
      onClick={onClick}
      className="absolute bottom-[38px] left-1/2 -translate-x-1/2 font-bold rounded-[10px] text-base border border-[1px] border-[#222222] bg-white w-[350px] h-[54px] flex justify-center items-center"
    >
      {label}
    </button>
  );
};

export default CommonBtn;
