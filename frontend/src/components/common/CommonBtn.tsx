type BtnProps = {
  label: string;
  notBottom?: boolean;
  className?: string;
  onClick: () => void;
};

const CommonBtn = ({
  label,
  onClick,
  className,
  notBottom = false,
}: BtnProps) => {
  return (
    <button
      onClick={onClick}
      className={`${
        notBottom ? "" : "absolute bottom-[38px] left-1/2 -translate-x-1/2"
      } font-bold rounded-[10px] text-base border border-[1px] w-[350px] h-[54px] flex justify-center items-center
      ${className ? className : "border-[#222222] bg-white"}`}
    >
      {label}
    </button>
  );
};

export default CommonBtn;
